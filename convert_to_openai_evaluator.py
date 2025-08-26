#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch configuration file conversion script
Functionality:
1. Replace qwen_evaluator with openai_evaluator configuration in all YAML files
2. Update field content if already using openai_evaluator
3. Support external configuration input or reading from JSON file
"""

import os
import yaml
import re
import json
import sys
from pathlib import Path
from typing import Dict, Any

def get_openai_evaluator_config(config_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Return standard openai_evaluator configuration
    Use provided config_data if available, otherwise use default configuration
    """
    if config_data:
        return config_data
    
    return {
        "class": "ApiModel",
        "name": "openai_evaluator",
        "config": {
            "provider": "openai",
            "model_identifier": "YOUR_MODEL",
            "api_key": "YOUR_API_KEY",
            "base_url": "YOUR_BASE_URL",
            "concurrency": 12
        }
    }

def main(external_config: Dict[str, Any] = None):
    """
    Main function: batch process all configuration files
    external_config: External configuration, use this if provided
    """
    # Get all YAML files in test directory
    test_dir = Path('./test')
    yaml_files = list(test_dir.glob('*.yaml'))
    
    if not yaml_files:
        print("❌ No YAML files found in test directory")
        return
    
    # Use external configuration if provided, otherwise use default
    target_config = get_openai_evaluator_config(external_config)
    
    print(f"Found {len(yaml_files)} YAML configuration files")
    if external_config:
        model_id = external_config.get('config', {}).get('model_identifier', 'unknown')
        print(f"Using external configuration, model: {model_id}")
    print("=" * 60)
    
    modified_yaml_count = 0
    total_yaml_count = len(yaml_files)
    
    # Process YAML files one by one
    for yaml_file in sorted(yaml_files):
        print(f"\nProcessing file: {yaml_file.name}")
        if update_yaml_config_with_target(yaml_file, target_config):
            modified_yaml_count += 1
    
    # Output summary
    print("\n" + "=" * 60)
    print(f"Processing completed!")
    print(f"Total YAML files: {total_yaml_count}")
    print(f"Modified YAML files: {modified_yaml_count}")
    print(f"Unmodified YAML files: {total_yaml_count - modified_yaml_count}")
    
    if modified_yaml_count > 0:
        model_id = target_config.get('config', {}).get('model_identifier', 'unknown')
        print(f"\n🎉 Conversion completed! Successfully updated configuration to model: {model_id}")
    else:
        print(f"\n✅ All files are already in target configuration, no modification needed.")

def update_yaml_config_with_target(file_path: Path, target_config: Dict[str, Any]) -> bool:
    """
    Update single YAML configuration file using specified target configuration
    """
    try:
        # Read YAML file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        modified = False
        
        # Check models configuration
        if 'models' in data:
            # Case 1: qwen_evaluator exists, need to replace with openai_evaluator
            if 'qwen_evaluator' in data['models']:
                # Remove original qwen_evaluator configuration
                del data['models']['qwen_evaluator']
                
                # Add new openai_evaluator configuration
                data['models']['openai_evaluator'] = target_config
                modified = True
                print(f"  ✓ Replaced qwen_evaluator with openai_evaluator")
            
            # Case 2: openai_evaluator already exists, update its field content
            elif 'openai_evaluator' in data['models']:
                existing_config = data['models']['openai_evaluator']
                
                # Check if there are actual changes
                if existing_config != target_config:
                    data['models']['openai_evaluator'] = target_config
                    modified = True
                else:
                    print(f"  - openai_evaluator configuration is already up to date, no update needed")
        
        # Check and update llm_model_name references in tasks
        if 'tasks' in data:
            # Handle tasks as dictionary
            if isinstance(data['tasks'], dict):
                for task_name, task_config in data['tasks'].items():
                    if isinstance(task_config, dict) and 'config' in task_config:
                        if task_config['config'].get('llm_model_name') == 'qwen_evaluator':
                            task_config['config']['llm_model_name'] = 'openai_evaluator'
                            modified = True
                            print(f"  ✓ Updated llm_model_name reference for task {task_name}")
            
            # Handle tasks as list
            elif isinstance(data['tasks'], list):
                for i, task_config in enumerate(data['tasks']):
                    if isinstance(task_config, dict) and 'config' in task_config:
                        if task_config['config'].get('llm_model_name') == 'qwen_evaluator':
                            task_config['config']['llm_model_name'] = 'openai_evaluator'
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

if __name__ == '__main__':
    # Check if configuration file is passed via command line arguments
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                external_config = json.load(f)
            main(external_config)
        except Exception as e:
            print(f"❌ Failed to read configuration file: {e}")
            sys.exit(1)
    else:
        main()