# -*- coding: utf-8 -*-
"""
Created on Wed Mar 16 17:07:43 2016

@author: jmjj
"""

import sys
import nose.tools
import tempfile
import messages2json
import shutil
import os
import json
import nose.plugins.capture
import io
import pathlib
from collections import OrderedDict

def sort_ordered_dict_helper(ordered_d: OrderedDict):
    '''
       Helper function for sorting the items of OrderedDict 
    '''
    
    return OrderedDict(sorted(ordered_d.items(), key=lambda t: t[0]))


class TestCmdLineProcessing():
    
    def __init__(self):
        self.tmp_input_file_name = ""
        self.tmp_output_file_name = ""
   
    def setup(self):
       '''
          Create a temporary file that contains messages in mbox format.
          Create a temporaray output file that is empty.
       '''

       self.tmp_input_file_name = tempfile.NamedTemporaryFile(mode='w+',delete=False).name
       self.tmp_output_file_name = tempfile.NamedTemporaryFile(mode='w+',delete=False).name

   
       shutil.copyfile('tests/test_messages_1.mbox',self.tmp_input_file_name)
       pathlib.Path(self.tmp_output_file_name).touch()

    def teardown(self):
       '''
          Remove the temporary input file and output files.
       '''
       
       os.remove(self.tmp_input_file_name) 
       os.remove(self.tmp_output_file_name) 
    
    def test_parse_cmd_line_args_1(self):
       '''
       Legal command line options are identified correctly.
       '''
       
       arg_string = '--input foo.ps --output gaa.hs --force --body'
       args = messages2json.parse_cmd_line_args(arg_string)
       nose.tools.assert_equal(args.in_f_or_d, 'foo.ps')    
       nose.tools.assert_equal(args.out_f_or_d, 'gaa.hs')     
       nose.tools.assert_true(args.force_save)
       nose.tools.assert_true(args.include_body)

    @nose.tools.raises(SystemExit)    
    def test_parse_cmd_line_args_2(self):
       '''
       Wrong command line option raieses exception.       
       '''
    
       arg_string = '--foola'
       messages2json.parse_cmd_line_args(arg_string)
    
    @nose.tools.raises(SystemExit)    
    def test_parse_cmd_line_args_3(self):
       '''
       Giving the command line option "--help" prints the help text.
       '''       
       capture_object = nose.plugins.capture.Capture()
       capture_object.begin()
       arg_string = '--help'
       messages2json.parse_cmd_line_args(arg_string) 
       capture_object.finalize()
       print(capture_object.buffer)
       nose.tools.assert_true(capture_object.buffer == "sfkdasdlfk")         
       

 
    def test_file_to_file_args_1(self):
       '''
       File to file command line option parsing works.        
       '''
       
       arg_string = '--input ' + self.tmp_input_file_name + ' --output ' + self.tmp_output_file_name
       print(arg_string)
       args = messages2json.parse_cmd_line_args(arg_string)
       nose.tools.assert_equal(args.in_f_or_d, self.tmp_input_file_name)
       nose.tools.assert_equal(args.out_f_or_d, self.tmp_output_file_name)
       
    def test_stdin_to_file_args_1(self):
       '''
       stdin to file command line option processing works.
       '''
       
       arg_string = '--output ' + self.tmp_output_file_name
       print(arg_string)
       args = messages2json.parse_cmd_line_args(arg_string)
       nose.tools.assert_equal(args.in_f_or_d, 'stdin')
       nose.tools.assert_equal(args.out_f_or_d, self.tmp_output_file_name)

    @nose.tools.raises(SystemExit)
    def test_process_files_2(self):
        '''
        Attempt to write JSON to existing file without the "--force" flag causes execption.        
        '''
        io_dict = {self.tmp_input_file_name:self.tmp_output_file_name}
        messages2json.process_files(io_dict, 'json', False, False)
        
       
    def test_process_files_1(self):
        '''
        Messages read from a file are correctly processed and stored to 
        an external file.
        '''            
        
        io_dict = {self.tmp_input_file_name:self.tmp_output_file_name}
        messages2json.process_files(io_dict, 'json', True, False)

        self.same_json_os = False        
        with open('tests/test_messages_1.result',mode='r') as file_o1:
            with open(self.tmp_output_file_name, mode='r') as file_o2:
                json_o1 = json.load(file_o1, strict=False, object_pairs_hook=OrderedDict)
                for k in json_o1.keys():
                    json_o1[k] = sort_ordered_dict_helper(json_o1[k])
                json_o2 = json.load(file_o2, strict=False, object_pairs_hook=OrderedDict)
                for k in json_o2.keys():
                    json_o2[k] = sort_ordered_dict_helper(json_o2[k])
          
                self.same_json_os = (json_o1 == json_o2) 
                
        nose.tools.assert_true(self.same_json_os)
        
    
    def test_process_files_3(self):
        '''
        Reading messages from stdin and writin result to extenal file.
        '''
        
        messages_to_stdin = open('tests/test_messages_1.mbox', mode='r').read()        
        io_dict = {'stdin':self.tmp_output_file_name}
        s = io.StringIO(messages_to_stdin)
        sys.stdin = s 
        messages2json.process_files(io_dict, 'json', True, False)
        sys.stdin = sys.__stdin__
        
        self.same_json_os = False        
        with open('tests/test_messages_1.result',mode='r') as file_o1:
            with open(self.tmp_output_file_name, mode='r') as file_o2:
                json_o1 = json.load(file_o1, strict=False, object_pairs_hook=OrderedDict)
                for k in json_o1.keys():
                    json_o1[k] = sort_ordered_dict_helper(json_o1[k])
                json_o2 = json.load(file_o2, strict=False, object_pairs_hook=OrderedDict)
                for k in json_o2.keys():
                    json_o2[k] = sort_ordered_dict_helper(json_o2[k])

                self.same_json_os = (json_o1 == json_o2)        
                
        nose.tools.assert_true(self.same_json_os)
        
        
    def test_process_files_4(self):
        '''
        Reading messages from external file and wrtitin JSON to stdout
        '''
        pass
    
    @nose.tools.raises(SystemExit) 
    def test_attempt_to_write_existing_file(self):
        '''
        '''
        
        io_dict = {self.tmp_input_file_name:self.tmp_output_file_name}
        messages2json.process_files(io_dict, 'json', False, False)

        self.same_json_os = False        
        with open('tests/test_messages_1.result',mode='r') as file_o1:
            with open(self.tmp_output_file_name, mode='r') as file_o2:
                json_o1_tmp = json.load(file_o1, strict=False, object_pairs_hook=OrderedDict)
                json_o2_tmp = json.load(file_o2, strict=False, object_pairs_hook=OrderedDict)
                json_o1 = []
                json_o2 = []
                for od in json_o1_tmp:
                    json_o1.append(sort_ordered_dict_helper(od))
                for od in json_o2_tmp:
                    json_o2.append(sort_ordered_dict_helper(od))
                print(json_o1)
   
                self.same_json_os = (json_o1 == json_o2) 
                
        nose.tools.assert_true(self.same_json_os)