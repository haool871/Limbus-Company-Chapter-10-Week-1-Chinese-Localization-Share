import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import localization_core as C
import versioned_sources as V
import batch_ops as B
import verify_retrans as Verify
import scope as Scope
import align_index as Align


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.kb=self.root/'kb'; self.kb.mkdir()
        self.kbpatch=patch.object(C,'KB',self.kb); self.kbpatch.start()
        self.game=self.root/'game'
        self.base=self.root/'base'
        self.loc=self.game/'LimbusCompany_Data/Assets/Resources_moved/Localize'
        for lang in C.LANGS: (self.loc/lang).mkdir(parents=True)
        C.save(self.base/'Info/version.json',{'version':1})
        self.set_source('kr','X.json',[{'id':1,'content':'원문 1'}])
        self.set_source('en','X.json',[{'id':1,'content':'Original 1'}])
        self.set_base('X.json',[{'id':1,'content':'原文1'}])
        self.old=self.root/'old'; V.capture(self.old,self.game,self.base)

    def tearDown(self):
        self.kbpatch.stop(); self.temp.cleanup()

    def set_source(self,lang,name,rows):
        p=Path(name)
        C.save(self.loc/lang/p.parent/(lang.upper()+'_'+p.name),{'dataList':rows})

    def set_base(self,name,rows): C.save(self.base/name,{'dataList':rows})

    def new(self):
        dest=self.root/'new'
        V.capture(dest,self.game,self.base)
        return dest

    def changed_batch(self,source='원문 2',extra_decision=None):
        self.set_source('kr','X.json',[{'id':1,'content':source}])
        new=self.new(); report=V.plan(self.old,new)
        dest=self.kb/'batches/test'
        B.create(dest,report,extra_decision)
        return dest

    def edit(self,batch,text='译文2',**kwargs):
        meta=C.load(batch/'batch.json'); row=meta['files']['X.json']['editable'][0]
        obj=C.load(batch/'patch/X.json')
        return {'file':'X.json','path':row['path'],'expected':C.get(obj,row['path']),
                'text':text,'reason':'逐条对照测试原文并复核上下文','semantic_review':True,'style_review':True,**kwargs}

    def test_source_same_count_number_change_detected(self):
        self.set_source('kr','X.json',[{'id':1,'content':'원문 2'}])
        report=V.plan(self.old,self.new())
        item=report['files'][0]
        self.assertEqual(item['changes']['kr']['fields'][0]['kind'],'modified')
        self.assertEqual(item['coverage'][0]['status'],'upstream_review')

    def test_equal_counts_different_id_detected(self):
        self.set_source('kr','X.json',[{'id':2,'content':'새로운'}])
        kinds=[x['kind'] for x in V.plan(self.old,self.new())['files'][0]['changes']['kr']['fields']]
        self.assertCountEqual(kinds,['added','deleted'])

    def test_kr_only_new_file_detected(self):
        self.set_source('kr','Only.json',[{'id':1,'content':'새로운'}])
        item=next(x for x in V.plan(self.old,self.new())['files'] if x['file']=='Only.json')
        self.assertEqual(item['source_language'],'kr')
        self.assertEqual(item['coverage'][0]['status'],'needs_translation')

    def test_duplicate_null_and_typed_ids_preserved(self):
        obj={'dataList':[{'id':1,'content':'a'},{'id':1,'content':'b'},{'id':None,'content':'c'},{'id':None,'content':'d'},{'id':'1','content':'e'}]}
        u=C.units(obj)
        self.assertEqual(len(u),5)
        self.assertEqual(sum(x['ambiguous'] for x in u.values()),4)
        self.assertEqual({tuple(x['path']) for x in u.values()},{('dataList',i,'content') for i in range(5)})

    def test_nested_indices_not_paired_by_list_position(self):
        a={'dataList':[{'key':'G','texts':[{'index':1,'text':'one'},{'index':2,'text':'two'}]}]}
        b=copy.deepcopy(a); b['dataList'][0]['texts'].reverse()
        changes=V.delta(a,b)
        self.assertEqual([x['kind'] for x in changes],['moved','moved'])
        self.assertTrue(all(x['old']['text']==x['new']['text'] for x in changes))

    def test_language_schema_difference_not_missing_dialogue(self):
        self.set_source('en','X.json',[{'id':1,'content':'Original 1','title':'Title'}])
        report=V.plan(self.old,self.new())
        self.assertEqual(report['history'],[])
        self.assertEqual(report['language_differences'][0]['en_only_paths'],[['dataList',0,'title']])
        self.assertEqual(report['files'][0]['coverage'][0]['status'],'inherited')

    def test_snapshot_immutable_hashes(self):
        (self.old/'kr/X.json').write_text('{}')
        with self.assertRaises(C.DataError): V.snapshot(self.old)

    def test_snapshot_refuses_overwrite(self):
        with self.assertRaises(C.DataError): V.capture(self.old,self.game,self.base)

    def test_snapshot_rejects_missing_official_directory(self):
        (self.loc/'jp').rmdir()
        with self.assertRaises(C.DataError): self.new()

    def test_source_deletion_requires_decision(self):
        for lang in ('kr','en'): (self.loc/lang/(lang.upper()+'_X.json')).unlink()
        self.set_source('kr','Other.json',[{'id':1,'content':'다른'}])
        report=V.plan(self.old,self.new())
        with self.assertRaises(C.DataError): B.create(self.kb/'batches/bad',report)
        dest=self.kb/'batches/ok'
        B.create(dest,report,{'X.json':{'action':'retire','reason':'官方已删除此文件'}})
        self.assertFalse((dest/'patch/X.json').exists())
        self.assertEqual(C.load(dest/'batch.json')['retired'][0]['file'],'X.json')

    def test_default_scope_read_only_and_empty_save_replaces_stale(self):
        self.set_source('kr','X.json',[{'id':1,'content':'원문 2'}]); new=self.new()
        with patch.object(sys,'argv',['scope','--old',str(self.old),'--new',str(new)]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(Scope.main(),0)
        self.assertFalse((self.kb/'terms/_review/scope.tsv').exists())
        output=self.root/'report.json'; C.save(output,{'stale':True})
        with patch.object(sys,'argv',['scope','--old',str(self.old),'--new',str(self.old),'--save',str(output)]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(Scope.main(),0)
        self.assertEqual(C.load(output)['files'],[])

    def test_unchanged_baseline_creates_no_batch(self):
        with self.assertRaises(C.DataError): B.create(self.kb/'batches/no',V.plan(self.old,self.old))
        self.assertFalse((self.kb/'batches/no').exists())

    def test_stale_scope_rejected(self):
        self.set_source('kr','X.json',[{'id':1,'content':'원문 2'}])
        report=V.plan(self.old,self.new()); report['files']=[]
        with self.assertRaises(C.DataError): B.create(self.kb/'batches/no',report)

    def test_history_not_silently_added_to_update(self):
        self.set_source('kr','History.json',[{'id':2,'content':'역사'}])
        histold=self.root/'histold'; V.capture(histold,self.game,self.base)
        self.set_source('kr','X.json',[{'id':1,'content':'원문 2'}])
        report=V.plan(histold,self.new())
        dest=self.kb/'batches/history'; B.create(dest,report)
        self.assertNotIn('History.json',C.load(dest/'batch.json')['files'])
        self.assertEqual(report['history'][0]['file'],'History.json')

    def test_template_uses_new_records_and_removes_old(self):
        self.set_source('kr','X.json',[{'id':2,'content':'새로운'}])
        report=V.plan(self.old,self.new())
        dest=self.kb/'batches/structure'
        B.create(dest,report,{'X.json':{'structure_reviewed':True,'reason':'已核对官方记录替换'}})
        self.assertEqual([x['id'] for x in C.load(dest/'patch/X.json')['dataList']],[2])

    def test_new_translation_is_checked_even_if_base_has_id(self):
        batch=self.changed_batch('<color=red>{0}</color> [Vibration]')
        with self.assertRaises(C.DataError): B.apply(batch,[self.edit(batch,'丢失标记')])

    def test_missing_field_rejected(self):
        batch=self.changed_batch()
        C.save(batch/'patch/X.json',{'dataList':[{'id':1}]})
        self.assertTrue(B.verify(batch)['errors'])

    def test_structural_metadata_protected(self):
        batch=self.changed_batch()
        obj=C.load(batch/'patch/X.json'); obj['dataList'][0]['id']=2
        C.save(batch/'patch/X.json',obj)
        self.assertTrue(any('受保护' in x for x in B.verify(batch)['errors']))

    def test_missing_source_and_invalid_json_fail(self):
        a=self.root/'source.json'; b=self.root/'bad.json'; b.write_text('{invalid')
        with self.assertRaises(C.DataError): Verify.compare_file(a,b)
        C.save(a,{'dataList':[]})
        with self.assertRaises(C.DataError): Verify.compare_file(a,b)

    def test_engine_token_placeholder_and_bad_tag_order_fail(self):
        self.assertTrue(C.text_errors('Gain [Vibration]','获得震颤'))
        self.assertTrue(C.text_errors('{0}','零'))
        self.assertTrue(C.text_errors('<color=red>one</color>','</color>一<color=red>'))
        self.assertTrue(C.text_errors('<b><i>x</i></b>','<b><i>字</b></i>'))

    def test_display_brackets_explicit_exception(self):
        self.assertTrue(C.text_errors('[Heathcliff]','[希斯克利夫]'))
        self.assertFalse(C.text_errors('[Heathcliff]','[希斯克利夫]',['Heathcliff']))

    def test_dante_angle_dialogue_not_html_italic(self):
        self.assertFalse(C.text_errors('<I think so.>','<我想是的。>'))

    def test_apply_and_byte_exact_rollback(self):
        batch=self.changed_batch(); before=(batch/'patch/X.json').read_bytes(); beforemeta=(batch/'batch.json').read_bytes()
        result=B.apply(batch,[self.edit(batch,'译文\n第二行\t含制表符')])
        self.assertFalse(B.verify(batch)['errors'])
        B.rollback(batch,result['transaction'])
        self.assertEqual((batch/'patch/X.json').read_bytes(),before)
        self.assertEqual((batch/'batch.json').read_bytes(),beforemeta)
        self.assertEqual(B.rollback(batch,result['transaction'])['status'],'already_reverted')

    def test_stale_expected_rejected(self):
        batch=self.changed_batch()
        with self.assertRaises(C.DataError): B.apply(batch,[self.edit(batch,expected='不匹配')])

    def test_dry_run_does_not_modify_translation(self):
        batch=self.changed_batch(); before=(batch/'patch/X.json').read_bytes()
        self.assertFalse(B.apply(batch,[self.edit(batch)],True)['written'])
        self.assertEqual((batch/'patch/X.json').read_bytes(),before)
        self.assertEqual(list((batch/'transactions').iterdir()),[])

    def test_review_hash_rejects_unreviewed_manual_edit(self):
        batch=self.changed_batch(); B.apply(batch,[self.edit(batch)])
        obj=C.load(batch/'patch/X.json'); obj['dataList'][0]['content']='未审校手改'
        C.save(batch/'patch/X.json',obj)
        self.assertTrue(any('审校' in x for x in B.verify(batch)['errors']))

    def test_second_edit_blocks_out_of_order_rollback(self):
        batch=self.changed_batch(); first=B.apply(batch,[self.edit(batch)])
        second=B.apply(batch,[self.edit(batch,'再次修改')])
        with self.assertRaises(C.DataError): B.rollback(batch,first['transaction'])
        B.rollback(batch,second['transaction']); B.rollback(batch,first['transaction'])

    def test_extra_unlisted_output_rejected(self):
        batch=self.changed_batch(); (batch/'patch/extra.json').write_text('{}')
        self.assertTrue(any('文件集合' in x for x in B.verify(batch)['errors']))

    def test_aligned_corpus_preserves_occurrences(self):
        corpus=self.root/'corpus.jsonl'; cache=self.root/'cache.pkl'
        rows=[{'f':'X','id':'1','record':f'id1:{i}','k':'content','l':'kr','t':str(i)} for i in range(2)]
        corpus.write_text(''.join(json.dumps(x)+'\n' for x in rows))
        with patch.object(Align,'CORPUS',str(corpus)),patch.object(Align,'CACHE',str(cache)):
            self.assertEqual(len(Align.build()),2)
        rows[1]['record']=rows[0]['record']; corpus.write_text(''.join(json.dumps(x)+'\n' for x in rows))
        with patch.object(Align,'CORPUS',str(corpus)),patch.object(Align,'CACHE',str(cache)):
            with self.assertRaises(ValueError): Align.build()

    def test_explicit_base_forms_equivalent(self):
        self.assertEqual(C.resolve_base(self.base),self.base.resolve())
        package=self.root/'package'; base=package/'LimbusCompany_Data/Lang/LLC_zh-CN'
        C.save(base/'Info/version.json',{'version':2})
        self.assertEqual(C.resolve_base(package),C.resolve_base(base))

    def test_waiting_checkers_never_claim_translation_pass(self):
        tools=Path(__file__).resolve().parents[1]/'tools'
        env={**os.environ,'LIMBUS_KB_ROOT':str(self.kb),'LIMBUS_BASE_PACK':str(self.base)}
        for name in ['verify_retrans.py','verify_output.py','check_speech_context.py']:
            p=subprocess.run([sys.executable,str(tools/name)],env=env,capture_output=True,text=True)
            self.assertEqual(p.returncode,2,(name,p.stdout,p.stderr))
            self.assertIn('无活动批次',p.stdout+p.stderr)
        self.assertFalse((self.kb/'patch_v2').exists())


    def test_upstream_new_source_still_requires_markers_and_review(self):
        self.set_source('kr','X.json',[{'id':1,'content':'{0} 새로운'}])
        report=V.plan(self.old,self.new())
        decision={'X.json':{'action':'upstream','reason':'已核对','semantic_reviewed':True,'style_reviewed':True}}
        with self.assertRaises(C.DataError): B.create(self.kb/'batches/upstream',report,decision)

    def test_new_field_is_written_and_rollback_restores_exact_bytes(self):
        self.set_source('kr','X.json',[{'id':1,'content':'원문 1','title':'새 제목'}])
        report=V.plan(self.old,self.new())
        dest=self.kb/'batches/title'
        B.create(dest,report,{'X.json':{'structure_reviewed':True,'reason':'新增标题供玩家显示'}})
        self.assertEqual(C.load(dest/'patch/X.json')['dataList'][0]['content'],'原文1')
        before=(dest/'patch/X.json').read_bytes()
        result=B.apply(dest,[self.edit(dest,'新标题')])
        self.assertEqual(C.load(dest/'patch/X.json')['dataList'][0]['title'],'新标题')
        B.rollback(dest,result['transaction'])
        self.assertEqual(before,(dest/'patch/X.json').read_bytes())

    def test_partial_transaction_can_be_recovered(self):
        batch=self.changed_batch(); before=(batch/'patch/X.json').read_bytes()
        real=C.atomic_bytes
        failed=False
        def failing(path,data):
            nonlocal failed
            if Path(path)==batch/'batch.json' and not failed:
                failed=True
                raise OSError('simulated interruption')
            return real(path,data)
        with patch.object(C,'atomic_bytes',failing):
            with self.assertRaises(OSError): B.apply(batch,[self.edit(batch)])
        self.assertEqual((batch/'patch/X.json').read_bytes(),before)
        with self.assertRaises(C.DataError): B.verify(batch)
        tid=next((batch/'transactions').iterdir()).name
        B.rollback(batch,tid)
        self.assertEqual((batch/'patch/X.json').read_bytes(),before)

    def test_cli_lifecycle_create_verify_export_finish(self):
        tools=Path(__file__).resolve().parents[1]/'tools'
        env={**os.environ,'LIMBUS_KB_ROOT':str(self.kb),'LIMBUS_BASE_PACK':str(self.base)}
        C.save(self.kb/'project.json',{'schema':1,'phase':'waiting','baseline':str(self.old),'active_batch':None})
        self.set_source('kr','X.json',[{'id':1,'content':'원문 2'}]); new=self.new()
        def cli(name,*args,expected=0):
            p=subprocess.run([sys.executable,str(tools/name),*map(str,args)],env=env,capture_output=True,text=True)
            self.assertEqual(p.returncode,expected,(name,p.stdout,p.stderr))
            return p
        report=self.root/'plan.json'
        cli('scope.py','--new',new,'--save',report)
        cli('batch.py','create','--name','lifecycle','--report',report)
        batch=self.kb/'batches/lifecycle'
        cli('batch.py','verify',expected=1)
        edits=self.root/'edits.json'; C.save(edits,[self.edit(batch)])
        cli('batch.py','apply','--edits',edits)
        cli('verify_output.py','--all')
        cli('batch.py','export','--out',self.root/'delivery')
        self.assertTrue((self.root/'delivery/delivery.json').is_file())
        cli('batch.py','finish')
        state=C.load(self.kb/'project.json')
        self.assertEqual(state['phase'],'waiting'); self.assertIsNone(state['active_batch'])
        self.assertEqual(Path(state['baseline']),new)
        self.assertFalse(batch.exists()); self.assertTrue((self.kb/'archives/batch_lifecycle/patch/X.json').exists())
        self.assertFalse((self.kb/'patch_v2').exists())

    def test_rpg_display_speaker_inherited_but_model_protected(self):
        rows=[{'key':'G','model':'internal','texts':[{'index':0,'speaker':'단테','text':'첫 말'}]}]
        self.set_source('kr','RPGSystem/Dialog.json',rows)
        self.set_base('RPGSystem/Dialog.json',[{'key':'G','model':'different','texts':[{'index':0,'speaker':'但丁','text':'原话'}]}])
        old=self.root/'rpgold'; V.capture(old,self.game,self.base)
        rows[0]['texts'][0]['text']='새 말'
        self.set_source('kr','RPGSystem/Dialog.json',rows)
        report=V.plan(old,self.new()); dest=self.kb/'batches/rpg'
        B.create(dest,report)
        obj=C.load(dest/'patch/RPGSystem/Dialog.json')
        self.assertEqual(obj['dataList'][0]['model'],'internal')
        self.assertEqual(obj['dataList'][0]['texts'][0]['speaker'],'但丁')
        entry=C.load(dest/'batch.json')['files']['RPGSystem/Dialog.json']
        self.assertEqual([r['path'][-1] for r in entry['editable']],['text'])
        obj['dataList'][0]['texts'][0]['speaker']='错误改名'; C.save(dest/'patch/RPGSystem/Dialog.json',obj)
        self.assertTrue(any('受保护' in e for e in B.verify(dest)['errors']))

    def test_unknown_rich_tag_and_dante_wrapper_preserved(self):
        self.assertTrue(C.text_errors('<sprite name="X"> 1','1'))
        self.assertFalse(C.text_errors('<sprite name="X"> 1','<sprite name="X"> 一'))
        self.assertTrue(C.text_errors('<I think so.>','我想是的。'))

    def test_source_falls_back_per_field_when_korean_is_empty(self):
        self.set_source('kr','X.json',[{'id':1,'content':'첫 문장'},{'id':2,'content':''}])
        self.set_source('en','X.json',[{'id':1,'content':'First'},{'id':2,'content':'Old English'}])
        self.set_base('X.json',[{'id':1,'content':'第一句'},{'id':2,'content':'旧英文译文'}])
        old=self.root/'mixedold'; V.capture(old,self.game,self.base)
        self.set_source('en','X.json',[{'id':1,'content':'First'},{'id':2,'content':'New English'}])
        report=V.plan(old,self.new()); dest=self.kb/'batches/mixed'
        B.create(dest,report)
        entry=C.load(dest/'batch.json')['files']['X.json']['editable'][0]
        self.assertEqual(entry['source_language'],'en')
        self.assertEqual(entry['source'],'New English')

    def test_explicit_english_schema_still_prefers_korean_semantics(self):
        self.set_source('kr','X.json',[{'id':1,'content':'새 한국어'}])
        self.set_source('en','X.json',[{'id':1,'content':'Changed English','title':'New title'}])
        report=V.plan(self.old,self.new()); dest=self.kb/'batches/englishschema'
        B.create(dest,report,{'X.json':{'schema_language':'en','structure_reviewed':True,'reason':'已核实英文独有title需要显示'}})
        entries=C.load(dest/'batch.json')['files']['X.json']['editable']
        self.assertEqual({r['path'][-1]:r['source_language'] for r in entries},{'content':'kr','title':'en'})

    def test_archived_batch_cannot_be_mutated_by_rollback(self):
        batch=self.changed_batch(); result=B.apply(batch,[self.edit(batch)])
        meta=C.load(batch/'batch.json'); meta['status']='archived'; C.save(batch/'batch.json',meta)
        before=(batch/'patch/X.json').read_bytes()
        with self.assertRaises(C.DataError): B.rollback(batch,result['transaction'])
        self.assertEqual(before,(batch/'patch/X.json').read_bytes())


if __name__=='__main__': unittest.main()
