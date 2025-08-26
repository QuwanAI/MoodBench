# -*- coding: utf-8 -*-

"""
Script for calculating weighted scores based on hierarchical weight configuration files
and distributed dataset evaluation results, generating merged dataset score JSON files.
"""

import os
import json
import yaml
import logging
import argparse
from typing import Dict, Any, Optional

# Configuration defaults
DEFAULT_OUTPUT_DIR = "result_analyze"
DEFAULT_BASE_RESULT_PATH = "./output/test"
DEFAULT_WEIGHT_CONFIG_FILE = "weight_config.yaml"
RESULT_FILENAME = "statistical_analysis/result_stats.json"
DEFAULT_SCORE = 70.0

SUCCESSFULLY_LOADED_DATASETS = set()

# Global variables
BASE_RESULT_PATH = DEFAULT_BASE_RESULT_PATH 

def setup_logging(log_file_path: str):
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, 'w', 'utf-8'),
            logging.StreamHandler()
        ],
        force=True
    )

def get_dataset_score(dataset_name: str, model_path: str) -> Optional[float]:
    """Get score by dataset name and model path. Returns None if file doesn't exist or parsing fails."""
    score_file_path = os.path.join(model_path, dataset_name, RESULT_FILENAME)
    if not os.path.exists(score_file_path):
        logging.warning(f"Result file not found: {dataset_name} (model: {os.path.basename(model_path)}). Dataset excluded from calculation")
        return None
    try:
        with open(score_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            first_value = next(iter(data.values()))
            if not isinstance(first_value, (int, float)):
                logging.error(f"First value in {score_file_path} is not numeric, dataset excluded from calculation")
                return None
            
            # Convert to percentage
            score_percentage = float(first_value) * 100
            SUCCESSFULLY_LOADED_DATASETS.add(dataset_name)
            return score_percentage
    except (json.JSONDecodeError, StopIteration, AttributeError) as e:
        logging.error(f"Failed to parse JSON file: {score_file_path}, error: {e}. Dataset excluded from calculation")
        return None

def calculate_scores(node: Dict[str, Any], node_name: str, model_path: str) -> Optional[float]:
    """
    Recursively calculate node scores using weighted average, excluding missing data.
    """
    # Case 1: Intermediate node with 'sub_tasks' dictionary
    if 'sub_tasks' in node and isinstance(node.get('sub_tasks'), dict):
        sub_tasks_node = node['sub_tasks']
        total_weighted_score_sum = 0.0
        total_weight_sum = 0.0
        has_valid_child = False

        for task_name, task_config in sub_tasks_node.items():
            child_score = None
            weight = 1.0

            if isinstance(task_config, dict):
                child_score = calculate_scores(task_config, task_name, model_path)
                weight = task_config.get('weight', 1.0)
            elif isinstance(task_config, (int, float)):
                child_score = get_dataset_score(task_name, model_path)
                weight = task_config

            # Only include in calculation when child_score is not None
            if child_score is not None:
                total_weighted_score_sum += child_score * weight
                total_weight_sum += weight
                has_valid_child = True
        
        if has_valid_child and total_weight_sum > 0:
            final_score = total_weighted_score_sum / total_weight_sum
            node['_score'] = final_score
            return final_score
        return None

    # Case 2: Leaf task not subdivided into datasets (only has 'weight' key)
    elif len(node) == 1 and 'weight' in node:
        logging.info(f"Task '{node_name}' not subdivided into datasets, excluded from calculation.")
        return None
    
    # Case 3: Bottom-level node with direct dataset:weight mappings
    else:
        total_weighted_score_sum = 0.0
        total_weight_sum = 0.0
        has_valid_child = False
        
        # Store dataset scores for reporting
        dataset_scores = {}
        
        for dataset_name, weight in node.items():
            if not isinstance(dataset_name, str) or not isinstance(weight, (int, float)):
                continue
            
            score = get_dataset_score(dataset_name, model_path)
            # Only include in calculation when score is not None
            if score is not None:
                dataset_scores[dataset_name] = score
                total_weighted_score_sum += score * weight
                total_weight_sum += weight
                has_valid_child = True
            else:
                # Record datasets not included in calculation
                dataset_scores[dataset_name] = None
        
        # Store dataset scores in node for report generation
        node['_dataset_scores'] = dataset_scores
        
        if has_valid_child and total_weight_sum > 0:
            final_score = total_weighted_score_sum / total_weight_sum
            node['_score'] = final_score
            return final_score
        return None

def collect_all_datasets(node: Dict[str, Any]) -> set:
    """
    Recursively collect all dataset names from configuration file
    """
    datasets = set()
    
    # Case 1: Intermediate node with 'sub_tasks' dictionary
    if 'sub_tasks' in node and isinstance(node.get('sub_tasks'), dict):
        for task_name, task_config in node['sub_tasks'].items():
            if isinstance(task_config, dict):
                datasets.update(collect_all_datasets(task_config))
            elif isinstance(task_config, (int, float)):
                # If task_config is numeric, task_name is a dataset name
                datasets.add(task_name)
    
    # Case 2: Bottom-level node with direct dataset:weight mappings
    else:
        for key, value in node.items():
            # Skip special keys
            if key in ['weight', 'sub_tasks', '_score', '_dataset_scores']:
                continue
            # If value is numeric, this is a dataset:weight configuration
            if isinstance(value, (int, float)):
                datasets.add(key)
    
    return datasets

def generate_model_datasets_json(model_path: str) -> Dict[str, float]:
    """
    Generate dictionary containing all dataset scores for a single model
    by directly traversing all dataset directories under model path
    """
    model_name = os.path.basename(model_path)
    logging.info(f"Processing model: {model_name}")
    
    # Directly traverse all directories under model path, each representing a dataset
    all_datasets = set()
    if os.path.exists(model_path):
        for item in os.listdir(model_path):
            item_path = os.path.join(model_path, item)
            if os.path.isdir(item_path):
                # Check if result file exists
                result_file = os.path.join(item_path, RESULT_FILENAME)
                if os.path.exists(result_file):
                    all_datasets.add(item)
    
    logging.info(f"Model {model_name} found {len(all_datasets)} datasets")
    
    # Get score for each dataset
    dataset_scores = {}
    for dataset_name in sorted(all_datasets):  # Sort for ordered output
        score = get_dataset_score(dataset_name, model_path)
        if score is not None:
            dataset_scores[dataset_name] = round(score, 2)  # Keep two decimal places
        else:
            dataset_scores[dataset_name] = -1  # Set missing scores to -1
    
    # Statistics
    valid_scores = sum(1 for score in dataset_scores.values() if score != -1)
    invalid_scores = len(dataset_scores) - valid_scores
    logging.info(f"Model {model_name} statistics: {valid_scores} valid scores, {invalid_scores} missing scores")
    
    return dataset_scores

def generate_all_models_json() -> None:
    """
    Traverse all models and generate merged dataset score JSON file
    """
    logging.info("Starting to traverse all models...")
    
    # Check if base path exists
    if not os.path.exists(BASE_RESULT_PATH):
        logging.error(f"Base result path does not exist: {BASE_RESULT_PATH}")
        return
    
    # Get all model directories
    model_dirs = []
    for item in os.listdir(BASE_RESULT_PATH):
        item_path = os.path.join(BASE_RESULT_PATH, item)
        if os.path.isdir(item_path):
            model_dirs.append(item_path)
    
    if not model_dirs:
        logging.error(f"No model directories found in {BASE_RESULT_PATH}")
        return
    
    logging.info(f"Found {len(model_dirs)} model directories")
    
    # Generate dataset scores for each model
    all_models_scores = {}
    for model_path in sorted(model_dirs):
        model_name = os.path.basename(model_path)
        logging.info(f"\n--- Processing model: {model_name} ---")
        
        # Reset global variable
        global SUCCESSFULLY_LOADED_DATASETS
        SUCCESSFULLY_LOADED_DATASETS = set()
        
        # Generate dataset scores for this model
        model_scores = generate_model_datasets_json(model_path)
        
        # Keep only valid scores (not -1)
        valid_scores = {k: v for k, v in model_scores.items() if v != -1}
        if valid_scores:
            all_models_scores[model_name] = valid_scores
            logging.info(f"Model {model_name} added {len(valid_scores)} valid dataset scores")
        else:
            logging.warning(f"Model {model_name} has no valid dataset scores")
    
    # Save merged JSON file
    output_file = os.path.join(DEFAULT_OUTPUT_DIR, "scores.json")
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_models_scores, f, ensure_ascii=False, indent=4)
    
    logging.info(f"\nMerged dataset score JSON file saved to: {output_file}")
    logging.info(f"Total processed models: {len(all_models_scores)}")

def main():
    """Main execution function"""
    # Setup and parse command line arguments
    parser = argparse.ArgumentParser(description="Traverse model directories and calculate dataset scores.")
    parser.add_argument(
        '--results_path',
        type=str,
        default=DEFAULT_BASE_RESULT_PATH,
        help=f"Root directory path for evaluation results. Default: {DEFAULT_BASE_RESULT_PATH}"
    )
    args = parser.parse_args()

    # Update global variable with command line argument or default
    global BASE_RESULT_PATH
    BASE_RESULT_PATH = args.results_path

    # Create output directory and configure logging
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
    setup_logging(os.path.join(DEFAULT_OUTPUT_DIR, "score_calculation.log"))
    
    logging.info("--- Starting calculation of dataset scores for all models ---")
    logging.info(f"Using result path: {BASE_RESULT_PATH}")
    
    # Generate dataset score JSON file for all models
    logging.info("Starting to generate dataset score JSON file for all models...")
    generate_all_models_json()
    
    logging.info("--- Analysis completed ---")


if __name__ == "__main__":
    main()