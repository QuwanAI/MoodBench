#!/bin/bash

# Automated test runner script
# Function: Loop through different model configurations to run tests

echo "🚀 Starting automated test process..."
echo "======================================"

# Configuration file paths
CONFIG_FILE="./model_configs.json"
CONVERT_SCRIPT="./convert_to_openai_evaluator.py"
TEST_SCRIPT="./run_all_tests.sh"
TEMP_CONFIG="./temp_config.json"

# Check if necessary files exist
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration file not found: $CONFIG_FILE"
    exit 1
fi

if [ ! -f "$CONVERT_SCRIPT" ]; then
    echo "❌ Convert script not found: $CONVERT_SCRIPT"
    exit 1
fi

if [ ! -f "$TEST_SCRIPT" ]; then
    echo "❌ Test script not found: $TEST_SCRIPT"
    exit 1
fi

# Ensure test script has execute permission
chmod +x "$TEST_SCRIPT"

# Read configuration count
config_count=$(python3 -c "import json; data=json.load(open('$CONFIG_FILE')); print(len(data))")
echo "📋 Found $config_count model configurations"

# Record start time
start_time=$(date +%s)
total_success=0
total_failed=0
failed_configs=()

# Loop through each configuration
for i in $(seq 0 $((config_count - 1))); do
    echo ""
    echo "======================================"
    echo "🔄 Processing configuration $((i + 1))/$config_count"
    echo "======================================"
    
    # Extract current configuration
    python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    configs = json.load(f)
with open('$TEMP_CONFIG', 'w') as f:
    json.dump(configs[$i], f, indent=2)
" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to extract configuration $((i + 1))"
        total_failed=$((total_failed + 1))
        failed_configs+=("Config$((i + 1)): extraction failed")
        continue
    fi
    
    # Get current configuration model identifier
    model_id=$(python3 -c "import json; data=json.load(open('$TEMP_CONFIG')); print(data.get('config', {}).get('model_identifier', 'unknown'))" 2>/dev/null)
    echo "📝 Current model: $model_id"
    
    # Step 1: Update configuration file
    echo "🔧 Step 1: Updating configuration file..."
    if python3 "$CONVERT_SCRIPT" "$TEMP_CONFIG"; then
        echo "✅ Configuration file updated successfully"
    else
        echo "❌ Configuration file update failed"
        total_failed=$((total_failed + 1))
        failed_configs+=("Config$((i + 1)): configuration update failed")
        continue
    fi
    
    # Step 2: Run tests
    echo "🧪 Step 2: Running test script..."
    if bash "$TEST_SCRIPT"; then
        echo "✅ Test execution successful - Model: $model_id"
        total_success=$((total_success + 1))
    else
        echo "❌ Test execution failed - Model: $model_id"
        total_failed=$((total_failed + 1))
        failed_configs+=("Config$((i + 1)): test execution failed (Model: $model_id)")
    fi
    
    # Clean up temporary files
    rm -f "$TEMP_CONFIG"
    
    echo "📊 Current progress: Success $total_success, Failed $total_failed"
done

# Record end time and calculate elapsed time
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))
elapsed_hours=$((elapsed_time / 3600))
elapsed_minutes=$(((elapsed_time % 3600) / 60))
elapsed_seconds=$((elapsed_time % 60))

# Output final summary
echo ""
echo "======================================"
echo "🎯 Automated test process completed!"
echo "======================================"
echo "📊 Execution statistics:"
echo "   Total configurations: $config_count"
echo "   Success: $total_success"
echo "   Failed: $total_failed"
echo "   Total time: ${elapsed_hours}h ${elapsed_minutes}m ${elapsed_seconds}s"

if [ $total_failed -gt 0 ]; then
    echo ""
    echo "❌ Failed configurations:"
    for failed_config in "${failed_configs[@]}"; do
        echo "   - $failed_config"
    done
    echo ""
    echo "⚠️  Please check failed configurations and logs"
else
    echo ""
    echo "🎉 All configurations executed successfully!"
    
    # Step 3: Calculate weighted scores
    echo ""
    echo "====================================="
    echo "📊 Step 3: Calculating weighted scores..."
    echo "====================================="
    if python calculate_weighted_scores.py; then
        echo "✅ Weighted scores calculated successfully"
        
        # Step 4: Generate report
        echo ""
        echo "====================================="
        echo "📋 Step 4: Generating analysis report..."
        echo "====================================="
        cd result_analyze
        if python generate_report.py result.xlsx scores.json report.html; then
            echo "✅ Analysis report generated successfully"
            echo "📄 Report file: result_analyze/report.html"
        else
            echo "❌ Analysis report generation failed"
        fi
        cd ..
    else
        echo "❌ Weighted scores calculation failed"
    fi
fi

if [ $total_failed -gt 0 ]; then
    exit 1
else
    exit 0
fi