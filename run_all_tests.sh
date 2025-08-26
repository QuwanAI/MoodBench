#!/bin/bash

# Batch execution script for all test configuration files
# Usage: ./run_all_tests.sh

echo "Starting execution of all test configuration files..."
echo "======================================"

# Define configuration file list
config_files=(
    "test_liangbiao1.yaml"
    "test_liangbiao2.yaml"
    "test_liangbiao8.yaml"
    "test_liangbiao9.yaml"
    "test_AGIEval.yaml"
    "test_AGNews.yaml"
    "test_BookSort.yaml"
    "test_C3.yaml"
    "test_CEval.yaml"
    "test_CMMLU.yaml"
    "test_CMRC.yaml"
    "test_CNewSum.yaml"
    "test_COPA.yaml"
    "test_CPED.yaml"
    "test_Cosmos.yaml"
    "test_Dianping.yaml"
    "test_EDOS.yaml"
    "test_EmoBenchA.yaml"
    "test_EmoBenchB.yaml"
    "test_EmoBenchC.yaml"
    "test_FOLIO.yaml"
    "test_GoEmotions.yaml"
    "test_HellaSwag.yaml"
    "test_IMDb.yaml"
    "test_LCQMC.yaml"
    "test_LogicNLI.yaml"
    "test_MMLU-pro.yaml"
    "test_MNLI.yaml"
    "test_MultiRC.yaml"
    "test_Mutual.yaml"
    "test_OCNLI.yaml"
    "test_PIQA.yaml"
    "test_PQEmotion1.yaml"
    "test_PQEmotion2.yaml"
    "test_PQEmotion3.yaml"
    "test_PQEmotion4.yaml"
    "test_PQEmotion5.yaml"
    "test_QQP.yaml"
    "test_RTE.yaml"
    "test_ReCoRD.yaml"
    "test_SAMSum.yaml"
    "test_SST-2.yaml"
    "test_SemEval.yaml"
    "test_SemEval1.yaml"
    "test_THUCNews.yaml"
    "test_TruthfulQA.yaml"
    "test_VCSUM.yaml"
    "test_VUA20.yaml"
    "test_WSC.yaml"
    "test_WiC.yaml"
    "test_lcsts.yaml"
    "test_SafetyBench1.yaml"
    "test_SafetyBench2.yaml"
    "test_SafetyBench3.yaml"
    "test_SafetyBench4.yaml"
    "test_SafetyBench5.yaml"
    "test_SafetyBench6.yaml"
    "test_SafetyBench7.yaml"
    "test_stereoset.yaml"
    "test_BBQ.yaml"
    "test_CrowS-Pairs.yaml"
    "test_longmemeval.yaml"
    "test_personafeeback.yaml"
)

# Record start time
start_time=$(date +%s)
total_files=${#config_files[@]}
current=0
success_count=0
failed_count=0
failed_files=()

# Execute configuration files one by one
for config_file in "${config_files[@]}"; do
    current=$((current + 1))
    echo "[$current/$total_files] Executing: $config_file"
    echo "Command: python ./src/PQAEF/run.py --config ./test/$config_file"
    
    # Execute command and capture return value
    if python ./src/PQAEF/run.py --config "./test/$config_file"; then
        echo "✅ $config_file executed successfully"
        success_count=$((success_count + 1))
    else
        echo "❌ $config_file execution failed"
        failed_count=$((failed_count + 1))
        failed_files+=("$config_file")
    fi
    
    echo "--------------------------------------"
done

# Record end time and calculate elapsed time
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))

# Output execution summary
echo "======================================"
echo "Execution completed!"
echo "Total files: $total_files"
echo "Success: $success_count"
echo "Failed: $failed_count"
echo "Total time: ${elapsed_time}s"

if [ $failed_count -gt 0 ]; then
    echo ""
    echo "Failed configuration files:"
    for failed_file in "${failed_files[@]}"; do
        echo "  - $failed_file"
    done
    exit 1
else
    echo "🎉 All configuration files executed successfully!"
    exit 0
fi
