## 🚀 欢迎来到 MoodBench

<div align="center"> <img src="./figure/logo.png" width="400px"> </div><div align="center"> <img src="./figure/quwan-1.png" width="90px"> <a href="./LICENSE"><img src="https://img.shields.io/badge/license-Apache%202-blueviolet.svg"></a> <a href="support os"><img src="https://img.shields.io/badge/os-linux%2C%20win%2C%20mac-pink.svg"></a> </div>


为了能够科学、系统地评估大语言模型的情感陪伴能力，**趣丸科技&北京大学-软件工程国家工程研究中心**联合推出了MoodBench评测基准。

我们严格基于[PQAEF](https://github.com/QuwanAI/PQAEF) 框架的“四维”理念（能力 -> 三级任务 -> 数据 -> 方法），对我们选取的一系列数据集进行了适配，如果你想测评垂域社交场景大语言模型的情感能力，相信MoodBench都能让这个过程变得轻而易举。

## 🛠️ 快速上手

只需三步，即可开始你的大模型情感能力评估之旅！

1. ### 下载代码

   Bash

   ```
   git clone https://github.com/QuwanAI/MoodBench.git
   cd /path/to/MoodBench
   ```

2. ### 配置环境 ⚙️

   Bash

   ```
   # 安装核心依赖
   pip install -r requirements.txt
   
   # 安装框架本身
   pip install -e .
   ```

3. ### 准备运行！

   🤖 配置待评估的模型

   在 `model_configs.json` 文件中，你可以配置任意数量的模型。脚本会自动逐一调用它们来接受评估。

   JSON

   ```
   [
       {
           "model_type": "api",
           "model_name": "openai_evaluator",
           "class": "ApiModel",
           "config": {
               "provider": "openai",
               "model_identifier": "YOUR_MODEL",
               "api_key": "YOUR_API_KEY",
               "base_url": "YOUR_BASE_URL",
               "concurrency": 1
           }
       }
   ]
   ```

   ▶️ 运行！

   一切准备就绪，运行下面的脚本！

   Bash

   ```
   sh ./run_all_tests_with_multi_models.sh
   ```

   🎉 **结果出炉**：你可以在 `result_analyze/results/` 目录下找到详细的评估报告。

------

## 🧩 新数据集集成指南

参考[PQAEF](https://github.com/QuwanAI/PQAEF)


## 👏🏻 License

This code repository is licensed under Apache-2.0 license, the corresponding dataset is licensed under CC BY-NC-SA 4.0.


## 🤝 贡献

发现了一个 bug？有一个绝妙的想法？或者开发了一个很酷的新功能？

请通过提交 **GitHub Issue** 来分享你的想法、建议或报告 bug。让我们共同努力，建设一个更好的 MoodBench！
