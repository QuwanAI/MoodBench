**1、基础能力**

①、自然语言理解（Natural Language Understand，NLU）：主要考察大模型是否能够有效解析和理解人类语言的含义和上下文内容。

②、自然语言生成（Natural Language Generation，NLG）：主要考察大模型是否能够根据给定的提示或条件自主生成连贯、符合语境的文本内容。

③、自然语言推理（Natural Language Inference，NLI）：主要考察大模型是否能够基于已有的信息进行逻辑推断和合理推测，以生成连贯且有意义的输出。

④、常识能力：主要考察模型是否能够理解并运用日常生活中的常见知识，包括物理世界的现象、社会规范、人类行为等。

**2、情感能力**

①、情感识别：

②、情感理解：

③、情感管理：

④、情感回复：

⑤、角色扮演：

⑥、对话能力：

**3、长期陪伴能力**

①、记忆管理能力：

②、个性化能力：

③、情感一致性：

④、用户满意度：

**4、外部知识获取能力**

①、外部知识库：

②、智能体：https://github.com/CLUEbenchmark/SuperCLUE-Agent?tab=readme-ov-file

**5、跨文化能力**

①、跨文化理解能力：

②、方言理解能力：

③、网络爆梗理解能力：

**6、多模态能力**

**7、价值观与安全**

①、价值观：

②、安全


<table border="1" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr>
      <th style="padding: 8px; text-align: left; background-color: #f2f2f2;">能力维度</th>
      <th style="padding: 8px; text-align: left; background-color: #f2f2f2;">能力名称</th>
      <th style="padding: 8px; text-align: left; background-color: #f2f2f2;">任务难度</th>
      <th style="padding: 8px; text-align: left; background-color: #f2f2f2;">评价任务</th>
      <th style="padding: 8px; text-align: left; background-color: #f2f2f2;">数据集</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="33">基础能力</td>
      <td rowspan="9">自然语言理解</td>
      <td rowspan="4">初级</td>
      <td rowspan="2">文本分类</td>
      <td>AGNews</td>
    </tr>
    <tr>
      <td>THUCNews</td>
    </tr>
    <tr>
      <td rowspan="2">文本匹配</td>
      <td>LCQMC</td>
    </tr>
    <tr>
      <td>QQP</td>
    </tr>
    <tr>
      <td rowspan="2">中级</td>
      <td>阅读理解（抽取式）</td>
      <td>CMRC</td>
    </tr>
    <tr>
      <td>词义消歧（多义词）</td>
      <td>WiC</td>
    </tr>
    <tr>
      <td rowspan="3">高级</td>
      <td rowspan="3">阅读理解</td>
      <td>C3</td>
    </tr>
    <tr>
      <td>MultiRC</td>
    </tr>
    <tr>
      <td>ReCoRD</td>
    </tr>
    <tr>
      <td rowspan="8">自然语言推理</td>
      <td rowspan="3">初级</td>
      <td rowspan="3">文本蕴含</td>
      <td>OCNLI</td>
    </tr>
    <tr>
      <td>MNLI</td>
    </tr>
    <tr>
      <td>RTE</td>
    </tr>
    <tr>
      <td rowspan="2">中级</td>
      <td>共指消解与常识推理</td>
      <td>WSC</td>
    </tr>
    <tr>
      <td>多轮对话推理</td>
      <td>Mutual</td>
    </tr>
    <tr>
      <td rowspan="3">高级</td>
      <td>因果推理</td>
      <td>COPA</td>
    </tr>
    <tr>
      <td>一阶逻辑推理</td>
      <td>FOLIO</td>
    </tr>
    <tr>
      <td>复杂逻辑推理</td>
      <td>LogicNLI</td>
    </tr>
    <tr>
      <td></td>
    </tr>
    <tr>
      <td rowspan="4">自然语言生成</td>
      <td rowspan="4">初级</td>
      <td rowspan="4">摘要</td>
      <td>lcsts</td>
    </tr>
    <tr>
      <td>SAMSum</td>
    </tr>
    <tr>
      <td>CNewSum</td>
    </tr>
    <tr>
      <td>VCSUM</td>
    </tr>
    <tr>
      <td rowspan="11">常识能力</td>
      <td rowspan="3">初级</td>
      <td>日常场景常识</td>
      <td>HellaSwag</td>
    </tr>
    <tr>
      <td>常识问答</td>
      <td>Cosmos</td>
    </tr>
    <tr>
      <td>物理常识</td>
      <td>PIQA</td>
    </tr>
    <tr>
      <td rowspan="4">中级</td>
      <td>人类认知与应试能力</td>
      <td>AGIEval</td>
    </tr>
    <tr>
      <td rowspan="3">多任务知识广度</td>
      <td>CMMLU</td>
    </tr>
    <tr>
      <td>MMLU-pro</td>
    </tr>
    <tr>
      <td>CEval</td>
    </tr>
    <tr>
      <td rowspan="4">高级</td>
      <td rowspan="4">真实性问答</td>
      <td rowspan="4">TruthfulQA</td>
    </tr>
    <tr>
      <td></td>
    </tr>
    <tr>
      <td></td>
    </tr>
    <tr>
      <td></td>
    </tr>
    <tr>
      <td rowspan="24">情感能力</td>
      <td rowspan="12">情感识别</td>
      <td rowspan="3">初级</td>
      <td rowspan="3">情感极性识别</td>
      <td>IMDb</td>
    </tr>
    <tr>
      <td>SST-2</td>
    </tr>
    <tr>
      <td>Dianping</td>
    </tr>
    <tr>
      <td rowspan="7">中级</td>
      <td rowspan="4">细粒度情感识别</td>
      <td>GoEmotions</td>
    </tr>
    <tr>
      <td>CPED</td>
    </tr>
    <tr>
      <td>EDOS</td>
    </tr>
    <tr>
      <td>PQEmotion1</td>
    </tr>
    <tr>
      <td>反讽识别</td>
      <td>SemEval-2018_Task_3</td>
    </tr>
    <tr>
      <td rowspan="2">隐喻识别</td>
      <td>VUA20</td>
    </tr>
    <tr>
      <td></td>
    </tr>
    <tr>
      <td>高级</td>
      <td>复杂情感识别</td>
      <td>EmoBench</td>
    </tr>
    <tr>
      <td></td>
    </tr>
    <tr>
      <td rowspan="3">情感理解</td>
      <td>初级</td>
      <td>情感强度理解</td>
      <td>SemEval-2018_Task_1</td>
    </tr>
    <tr>
      <td rowspan="2">中级</td>
      <td rowspan="2">情感原因分析</td>
      <td>PQEmotion2</td>
    </tr>
    <tr>
      <td>EmoBench</td>
    </tr>
    <tr>
      <td>情感管理</td>
      <td>中级</td>
      <td>情感策略选择</td>
      <td>PQEmotion3</td>
    </tr>
    <tr>
      <td rowspan="4">情感回复</td>
      <td rowspan="2">中级</td>
      <td rowspan="2">共情表达</td>
      <td>EmoBench</td>
    </tr>
    <tr>
      <td>PQEmotion4</td>
    </tr>
    <tr>
      <td rowspan="2">高级</td>
      <td>特定场景下情感回复</td>
      <td>PQEmotion5</td>
    </tr>
    <tr>
      <td>个性化情感回复</td>
      <td>CPED</td>
    </tr>
    <tr>
      <td rowspan="4">综合情感智能</td>
      <td>初级</td>
      <td>有效沟通能力测试</td>
      <td>liangbiao2 有效沟通测试</td>
    </tr>
    <tr>
      <td>中级</td>
      <td>人际关系处理能力测试</td>
      <td>liangbiao1 人际关系测试</td>
    </tr>
    <tr>
      <td rowspan="2">高级</td>
      <td rowspan="2">情商测试</td>
      <td>liangbiao8 EQ-60 共情商量表</td>
    </tr>
    <tr>
      <td>liangbiao9 IRI30 项情商问卷</td>
    </tr>
    <tr>
      <td rowspan="4">陪伴能力</td>
      <td rowspan="2">记忆管理能力</td>
      <td>初级</td>
      <td>序列顺序回忆</td>
      <td>BookSort</td>
    </tr>
    <tr>
      <td>高级</td>
      <td>长期对话回忆</td>
      <td>LongMemEval</td>
    </tr>
    <tr>
      <td rowspan="2">个性化能力</td>
      <td>初级</td>
      <td>个性化程度</td>
      <td>PersonaFeedback</td>
    </tr>
    <tr>
      <td>中级</td>
      <td>个性化情感回复</td>
      <td>CPED</td>
    </tr>
    <tr>
      <td rowspan="10">价值观与安全</td>
      <td rowspan="5">价值观</td>
      <td rowspan="4">初级</td>
      <td rowspan="4">偏见检测</td>
      <td>CrowS-Pairs</td>
    </tr>
    <tr>
      <td>StereoSet</td>
    </tr>
    <tr>
      <td>BBQ</td>
    </tr>
    <tr>
      <td>SafetyBench7-Unfairness and Bias</td>
    </tr>
    <tr>
      <td>中级</td>
      <td>道德检测</td>
      <td>SafetyBench1-Ethics and Morality</td>
    </tr>
    <tr>
      <td rowspan="5">安全</td>
      <td>初级</td>
      <td>内容安全</td>
      <td>SafetyBench3-Offensiveness</td>
    </tr>
    <tr>
      <td rowspan="4">中级</td>
      <td>信息安全</td>
      <td>SafetyBench4-Privacy and Property</td>
    </tr>
    <tr>
      <td rowspan="2">用户安全</td>
      <td>SafetyBench2-Mental Health</td>
    </tr>
    <tr>
      <td>SafetyBench6-Physical Health</td>
    </tr>
    <tr>
      <td>高风险危害行为</td>
      <td>SafetyBench5-Illegal Activities</td>
    </tr>
  </tbody>
</table>

