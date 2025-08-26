#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch configuration file conversion script (API model to local model)
Functionality:
1. Replace openai_evaluator with qwen_evaluator configuration in all YAML files
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

def get_qwen_evaluator_config() -> Dict[str, Any]:
    """
    Return standard qwen_evaluator local model configuration
    """
    return {
        "class": "LocalModel",
        "name": "qwen_evaluator_llm",
        "config": {
            "model_path": "/mnt/data/model/Qwen2.5-7B-Instruct",  # Default model path
            "batch_size": 32,
            "device_ids": [6, 7],
            "model_kwargs": {
                "torch_dtype": "bfloat16",
                "attn_implementation": "sdpa"
            },
            "generation_kwargs": {
                "max_new_tokens": 50,
                "temperature": 0.1,
                "top_p": 0.95
            }
        }
    }

def update_yaml_config(file_path: Path, custom_model_path: str = None) -> bool:
    """
    Update single YAML configuration file, replace openai_evaluator with qwen_evaluator
    """
    try:
        # Read YAML file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        modified = False
        
        # Check and replace openai_evaluator in models
        if 'models' in data and 'openai_evaluator' in data['models']:
            # Remove original openai_evaluator configuration
            del data['models']['openai_evaluator']
            
            # Add new qwen_evaluator configuration
            qwen_config = get_qwen_evaluator_config()
            if custom_model_path:
                qwen_config['config']['model_path'] = custom_model_path
            
            data['models']['qwen_evaluator'] = qwen_config
            modified = True
            print(f"  ✓ Replaced openai_evaluator with qwen_evaluator")
            if custom_model_path:
                print(f"  ✓ Using custom model path: {custom_model_path}")
        
        # Check and update llm_model_name references in tasks
        if 'tasks' in data:
            # Handle tasks as dictionary
            if isinstance(data['tasks'], dict):
                for task_name, task_config in data['tasks'].items():
                    if isinstance(task_config, dict) and 'config' in task_config:
                        if task_config['config'].get('llm_model_name') == 'openai_evaluator':
                            task_config['config']['llm_model_name'] = 'qwen_evaluator'
                            modified = True
                            print(f"  ✓ Updated llm_model_name reference for task {task_name}")
            
            # Handle tasks as list
            elif isinstance(data['tasks'], list):
                for i, task_config in enumerate(data['tasks']):
                    if isinstance(task_config, dict) and 'config' in task_config:
                        if task_config['config'].get('llm_model_name') == 'openai_evaluator':
                            task_config['config']['llm_model_name'] = 'qwen_evaluator'
                            modified = True
                            print(f"  ✓ Updated llm_model_name reference for task list item {i+1}")
        
        # Write back to file if modified
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, 
                         sort_keys=False, indent=2)
            return True
        else:
            print(f"  - No modification needed")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing file: {e}")
        return False

def main():
    """
    Main function: batch process all configuration files
    """
    import argparse
    
    # Add command line argument parsing
    parser = argparse.ArgumentParser(description='Batch convert API model configuration to local model configuration')
    parser.add_argument(
        '--model-path', 
        type=str, 
        help='Custom local model path, defaults to /mnt/data/model/Qwen2.5-7B-Instruct if not specified'
    )
    
    args = parser.parse_args()
    
    # Get all YAML files in test directory
    test_dir = Path('./test')
    yaml_files = list(test_dir.glob('*.yaml'))
    
    if not yaml_files:
        print("❌ No YAML files found in test directory")
        return
    
    print(f"Found {len(yaml_files)} YAML configuration files")
    print("Configuration parameters:")
    print(f"  - Target model: qwen_evaluator (local model)")
    print(f"  - Model path: {args.model_path or '/mnt/data/model/Qwen2.5-7B-Instruct (default)'}")
    print(f"  - batch_size: 32")
    print(f"  - device_ids: [6, 7]")
    print("=" * 60)
    
    modified_yaml_count = 0
    total_yaml_count = len(yaml_files)
    
    # Process YAML files one by one
    for yaml_file in sorted(yaml_files):
        print(f"\nProcessing file: {yaml_file.name}")
        if update_yaml_config(yaml_file, args.model_path):
            modified_yaml_count += 1
    
    # Output summary
    print("\n" + "=" * 60)
    print(f"Processing completed!")
    print(f"Total YAML files: {total_yaml_count}")
    print(f"Modified YAML files: {modified_yaml_count}")
    print(f"Unmodified YAML files: {total_yaml_count - modified_yaml_count}")
    
    if modified_yaml_count > 0:
        print(f"\n🎉 Conversion completed! Successfully converted configuration from openai_evaluator to qwen_evaluator")
        print("\n⚠️  Please note:")
        print("   1. Ensure the specified model path exists and is accessible")
        print("   2. Adjust device_ids parameter according to your GPU configuration")
        print("   3. Adjust batch_size parameter according to memory size")
        print("   4. Ensure local model dependency libraries are installed")
    else:
        print(f"\n✅ All files are already in target configuration, no modification needed.")

if __name__ == '__main__':
    main()