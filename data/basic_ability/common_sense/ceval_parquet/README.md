---
license: cc-by-nc-sa-4.0
task_categories:
- text-classification
- multiple-choice
- question-answering
language:
- zh
pretty_name: C-Eval
size_categories:
- 10K<n<100K
configs:
- config_name: accountant
  data_files:
  - split: test
    path: accountant/test-*
  - split: val
    path: accountant/val-*
  - split: dev
    path: accountant/dev-*
- config_name: advanced_mathematics
  data_files:
  - split: test
    path: advanced_mathematics/test-*
  - split: val
    path: advanced_mathematics/val-*
  - split: dev
    path: advanced_mathematics/dev-*
- config_name: art_studies
  data_files:
  - split: test
    path: art_studies/test-*
  - split: val
    path: art_studies/val-*
  - split: dev
    path: art_studies/dev-*
- config_name: basic_medicine
  data_files:
  - split: test
    path: basic_medicine/test-*
  - split: val
    path: basic_medicine/val-*
  - split: dev
    path: basic_medicine/dev-*
- config_name: business_administration
  data_files:
  - split: test
    path: business_administration/test-*
  - split: val
    path: business_administration/val-*
  - split: dev
    path: business_administration/dev-*
- config_name: chinese_language_and_literature
  data_files:
  - split: test
    path: chinese_language_and_literature/test-*
  - split: val
    path: chinese_language_and_literature/val-*
  - split: dev
    path: chinese_language_and_literature/dev-*
- config_name: civil_servant
  data_files:
  - split: test
    path: civil_servant/test-*
  - split: val
    path: civil_servant/val-*
  - split: dev
    path: civil_servant/dev-*
- config_name: clinical_medicine
  data_files:
  - split: test
    path: clinical_medicine/test-*
  - split: val
    path: clinical_medicine/val-*
  - split: dev
    path: clinical_medicine/dev-*
- config_name: college_chemistry
  data_files:
  - split: test
    path: college_chemistry/test-*
  - split: val
    path: college_chemistry/val-*
  - split: dev
    path: college_chemistry/dev-*
- config_name: college_economics
  data_files:
  - split: test
    path: college_economics/test-*
  - split: val
    path: college_economics/val-*
  - split: dev
    path: college_economics/dev-*
- config_name: college_physics
  data_files:
  - split: test
    path: college_physics/test-*
  - split: val
    path: college_physics/val-*
  - split: dev
    path: college_physics/dev-*
- config_name: college_programming
  data_files:
  - split: test
    path: college_programming/test-*
  - split: val
    path: college_programming/val-*
  - split: dev
    path: college_programming/dev-*
- config_name: computer_architecture
  data_files:
  - split: test
    path: computer_architecture/test-*
  - split: val
    path: computer_architecture/val-*
  - split: dev
    path: computer_architecture/dev-*
- config_name: computer_network
  data_files:
  - split: test
    path: computer_network/test-*
  - split: val
    path: computer_network/val-*
  - split: dev
    path: computer_network/dev-*
- config_name: discrete_mathematics
  data_files:
  - split: test
    path: discrete_mathematics/test-*
  - split: val
    path: discrete_mathematics/val-*
  - split: dev
    path: discrete_mathematics/dev-*
- config_name: education_science
  data_files:
  - split: test
    path: education_science/test-*
  - split: val
    path: education_science/val-*
  - split: dev
    path: education_science/dev-*
- config_name: electrical_engineer
  data_files:
  - split: test
    path: electrical_engineer/test-*
  - split: val
    path: electrical_engineer/val-*
  - split: dev
    path: electrical_engineer/dev-*
- config_name: environmental_impact_assessment_engineer
  data_files:
  - split: test
    path: environmental_impact_assessment_engineer/test-*
  - split: val
    path: environmental_impact_assessment_engineer/val-*
  - split: dev
    path: environmental_impact_assessment_engineer/dev-*
- config_name: fire_engineer
  data_files:
  - split: test
    path: fire_engineer/test-*
  - split: val
    path: fire_engineer/val-*
  - split: dev
    path: fire_engineer/dev-*
- config_name: high_school_biology
  data_files:
  - split: test
    path: high_school_biology/test-*
  - split: val
    path: high_school_biology/val-*
  - split: dev
    path: high_school_biology/dev-*
- config_name: high_school_chemistry
  data_files:
  - split: test
    path: high_school_chemistry/test-*
  - split: val
    path: high_school_chemistry/val-*
  - split: dev
    path: high_school_chemistry/dev-*
- config_name: high_school_chinese
  data_files:
  - split: test
    path: high_school_chinese/test-*
  - split: val
    path: high_school_chinese/val-*
  - split: dev
    path: high_school_chinese/dev-*
- config_name: high_school_geography
  data_files:
  - split: test
    path: high_school_geography/test-*
  - split: val
    path: high_school_geography/val-*
  - split: dev
    path: high_school_geography/dev-*
- config_name: high_school_history
  data_files:
  - split: test
    path: high_school_history/test-*
  - split: val
    path: high_school_history/val-*
  - split: dev
    path: high_school_history/dev-*
- config_name: high_school_mathematics
  data_files:
  - split: test
    path: high_school_mathematics/test-*
  - split: val
    path: high_school_mathematics/val-*
  - split: dev
    path: high_school_mathematics/dev-*
- config_name: high_school_physics
  data_files:
  - split: test
    path: high_school_physics/test-*
  - split: val
    path: high_school_physics/val-*
  - split: dev
    path: high_school_physics/dev-*
- config_name: high_school_politics
  data_files:
  - split: test
    path: high_school_politics/test-*
  - split: val
    path: high_school_politics/val-*
  - split: dev
    path: high_school_politics/dev-*
- config_name: ideological_and_moral_cultivation
  data_files:
  - split: test
    path: ideological_and_moral_cultivation/test-*
  - split: val
    path: ideological_and_moral_cultivation/val-*
  - split: dev
    path: ideological_and_moral_cultivation/dev-*
- config_name: law
  data_files:
  - split: test
    path: law/test-*
  - split: val
    path: law/val-*
  - split: dev
    path: law/dev-*
- config_name: legal_professional
  data_files:
  - split: test
    path: legal_professional/test-*
  - split: val
    path: legal_professional/val-*
  - split: dev
    path: legal_professional/dev-*
- config_name: logic
  data_files:
  - split: test
    path: logic/test-*
  - split: val
    path: logic/val-*
  - split: dev
    path: logic/dev-*
- config_name: mao_zedong_thought
  data_files:
  - split: test
    path: mao_zedong_thought/test-*
  - split: val
    path: mao_zedong_thought/val-*
  - split: dev
    path: mao_zedong_thought/dev-*
- config_name: marxism
  data_files:
  - split: test
    path: marxism/test-*
  - split: val
    path: marxism/val-*
  - split: dev
    path: marxism/dev-*
- config_name: metrology_engineer
  data_files:
  - split: test
    path: metrology_engineer/test-*
  - split: val
    path: metrology_engineer/val-*
  - split: dev
    path: metrology_engineer/dev-*
- config_name: middle_school_biology
  data_files:
  - split: test
    path: middle_school_biology/test-*
  - split: val
    path: middle_school_biology/val-*
  - split: dev
    path: middle_school_biology/dev-*
- config_name: middle_school_chemistry
  data_files:
  - split: test
    path: middle_school_chemistry/test-*
  - split: val
    path: middle_school_chemistry/val-*
  - split: dev
    path: middle_school_chemistry/dev-*
- config_name: middle_school_geography
  data_files:
  - split: test
    path: middle_school_geography/test-*
  - split: val
    path: middle_school_geography/val-*
  - split: dev
    path: middle_school_geography/dev-*
- config_name: middle_school_history
  data_files:
  - split: test
    path: middle_school_history/test-*
  - split: val
    path: middle_school_history/val-*
  - split: dev
    path: middle_school_history/dev-*
- config_name: middle_school_mathematics
  data_files:
  - split: test
    path: middle_school_mathematics/test-*
  - split: val
    path: middle_school_mathematics/val-*
  - split: dev
    path: middle_school_mathematics/dev-*
- config_name: middle_school_physics
  data_files:
  - split: test
    path: middle_school_physics/test-*
  - split: val
    path: middle_school_physics/val-*
  - split: dev
    path: middle_school_physics/dev-*
- config_name: middle_school_politics
  data_files:
  - split: test
    path: middle_school_politics/test-*
  - split: val
    path: middle_school_politics/val-*
  - split: dev
    path: middle_school_politics/dev-*
- config_name: modern_chinese_history
  data_files:
  - split: test
    path: modern_chinese_history/test-*
  - split: val
    path: modern_chinese_history/val-*
  - split: dev
    path: modern_chinese_history/dev-*
- config_name: operating_system
  data_files:
  - split: test
    path: operating_system/test-*
  - split: val
    path: operating_system/val-*
  - split: dev
    path: operating_system/dev-*
- config_name: physician
  data_files:
  - split: test
    path: physician/test-*
  - split: val
    path: physician/val-*
  - split: dev
    path: physician/dev-*
- config_name: plant_protection
  data_files:
  - split: test
    path: plant_protection/test-*
  - split: val
    path: plant_protection/val-*
  - split: dev
    path: plant_protection/dev-*
- config_name: probability_and_statistics
  data_files:
  - split: test
    path: probability_and_statistics/test-*
  - split: val
    path: probability_and_statistics/val-*
  - split: dev
    path: probability_and_statistics/dev-*
- config_name: professional_tour_guide
  data_files:
  - split: test
    path: professional_tour_guide/test-*
  - split: val
    path: professional_tour_guide/val-*
  - split: dev
    path: professional_tour_guide/dev-*
- config_name: sports_science
  data_files:
  - split: test
    path: sports_science/test-*
  - split: val
    path: sports_science/val-*
  - split: dev
    path: sports_science/dev-*
- config_name: tax_accountant
  data_files:
  - split: test
    path: tax_accountant/test-*
  - split: val
    path: tax_accountant/val-*
  - split: dev
    path: tax_accountant/dev-*
- config_name: teacher_qualification
  data_files:
  - split: test
    path: teacher_qualification/test-*
  - split: val
    path: teacher_qualification/val-*
  - split: dev
    path: teacher_qualification/dev-*
- config_name: urban_and_rural_planner
  data_files:
  - split: test
    path: urban_and_rural_planner/test-*
  - split: val
    path: urban_and_rural_planner/val-*
  - split: dev
    path: urban_and_rural_planner/dev-*
- config_name: veterinary_medicine
  data_files:
  - split: test
    path: veterinary_medicine/test-*
  - split: val
    path: veterinary_medicine/val-*
  - split: dev
    path: veterinary_medicine/dev-*
dataset_info:
- config_name: accountant
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 176917
    num_examples: 443
  - name: val
    num_bytes: 19549
    num_examples: 49
  - name: dev
    num_bytes: 3414
    num_examples: 5
  download_size: 151233
  dataset_size: 199880
- config_name: advanced_mathematics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 50031
    num_examples: 173
  - name: val
    num_bytes: 5331
    num_examples: 19
  - name: dev
    num_bytes: 7012
    num_examples: 5
  download_size: 50962
  dataset_size: 62374
- config_name: art_studies
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 41227
    num_examples: 298
  - name: val
    num_bytes: 4581
    num_examples: 33
  - name: dev
    num_bytes: 1439
    num_examples: 5
  download_size: 46524
  dataset_size: 47247
- config_name: basic_medicine
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 28820
    num_examples: 175
  - name: val
    num_bytes: 2627
    num_examples: 19
  - name: dev
    num_bytes: 1825
    num_examples: 5
  download_size: 37360
  dataset_size: 33272
- config_name: business_administration
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 78387
    num_examples: 301
  - name: val
    num_bytes: 9225
    num_examples: 33
  - name: dev
    num_bytes: 3155
    num_examples: 5
  download_size: 75885
  dataset_size: 90767
- config_name: chinese_language_and_literature
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 32328
    num_examples: 209
  - name: val
    num_bytes: 3446
    num_examples: 23
  - name: dev
    num_bytes: 1892
    num_examples: 5
  download_size: 42310
  dataset_size: 37666
- config_name: civil_servant
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 181504
    num_examples: 429
  - name: val
    num_bytes: 21273
    num_examples: 47
  - name: dev
    num_bytes: 4576
    num_examples: 5
  download_size: 179936
  dataset_size: 207353
- config_name: clinical_medicine
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 42161
    num_examples: 200
  - name: val
    num_bytes: 4167
    num_examples: 22
  - name: dev
    num_bytes: 1951
    num_examples: 5
  download_size: 48689
  dataset_size: 48279
- config_name: college_chemistry
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 45798
    num_examples: 224
  - name: val
    num_bytes: 4443
    num_examples: 24
  - name: dev
    num_bytes: 3611
    num_examples: 5
  download_size: 53519
  dataset_size: 53852
- config_name: college_economics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 119734
    num_examples: 497
  - name: val
    num_bytes: 14461
    num_examples: 55
  - name: dev
    num_bytes: 3673
    num_examples: 5
  download_size: 106080
  dataset_size: 137868
- config_name: college_physics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 55731
    num_examples: 176
  - name: val
    num_bytes: 6145
    num_examples: 19
  - name: dev
    num_bytes: 3824
    num_examples: 5
  download_size: 62877
  dataset_size: 65700
- config_name: college_programming
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 83541
    num_examples: 342
  - name: val
    num_bytes: 9543
    num_examples: 37
  - name: dev
    num_bytes: 2882
    num_examples: 5
  download_size: 82850
  dataset_size: 95966
- config_name: computer_architecture
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 40613
    num_examples: 193
  - name: val
    num_bytes: 4149
    num_examples: 21
  - name: dev
    num_bytes: 2793
    num_examples: 5
  download_size: 48021
  dataset_size: 47555
- config_name: computer_network
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 35408
    num_examples: 171
  - name: val
    num_bytes: 3799
    num_examples: 19
  - name: dev
    num_bytes: 2361
    num_examples: 5
  download_size: 43940
  dataset_size: 41568
- config_name: discrete_mathematics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 36045
    num_examples: 153
  - name: val
    num_bytes: 3424
    num_examples: 16
  - name: dev
    num_bytes: 2002
    num_examples: 5
  download_size: 42941
  dataset_size: 41471
- config_name: education_science
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 55753
    num_examples: 270
  - name: val
    num_bytes: 5519
    num_examples: 29
  - name: dev
    num_bytes: 3093
    num_examples: 5
  download_size: 60878
  dataset_size: 64365
- config_name: electrical_engineer
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 73727
    num_examples: 339
  - name: val
    num_bytes: 8315
    num_examples: 37
  - name: dev
    num_bytes: 2180
    num_examples: 5
  download_size: 75493
  dataset_size: 84222
- config_name: environmental_impact_assessment_engineer
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 84680
    num_examples: 281
  - name: val
    num_bytes: 9186
    num_examples: 31
  - name: dev
    num_bytes: 2495
    num_examples: 5
  download_size: 73938
  dataset_size: 96361
- config_name: fire_engineer
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 83611
    num_examples: 282
  - name: val
    num_bytes: 9998
    num_examples: 31
  - name: dev
    num_bytes: 2209
    num_examples: 5
  download_size: 80027
  dataset_size: 95818
- config_name: high_school_biology
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 55242
    num_examples: 175
  - name: val
    num_bytes: 6105
    num_examples: 19
  - name: dev
    num_bytes: 2164
    num_examples: 5
  download_size: 60521
  dataset_size: 63511
- config_name: high_school_chemistry
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 46918
    num_examples: 172
  - name: val
    num_bytes: 5625
    num_examples: 19
  - name: dev
    num_bytes: 2576
    num_examples: 5
  download_size: 55668
  dataset_size: 55119
- config_name: high_school_chinese
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 110347
    num_examples: 178
  - name: val
    num_bytes: 10475
    num_examples: 19
  - name: dev
    num_bytes: 5290
    num_examples: 5
  download_size: 121511
  dataset_size: 126112
- config_name: high_school_geography
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 41244
    num_examples: 178
  - name: val
    num_bytes: 3985
    num_examples: 19
  - name: dev
    num_bytes: 2087
    num_examples: 5
  download_size: 49899
  dataset_size: 47316
- config_name: high_school_history
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 56196
    num_examples: 182
  - name: val
    num_bytes: 6618
    num_examples: 20
  - name: dev
    num_bytes: 2421
    num_examples: 5
  download_size: 68541
  dataset_size: 65235
- config_name: high_school_mathematics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 41080
    num_examples: 166
  - name: val
    num_bytes: 5144
    num_examples: 18
  - name: dev
    num_bytes: 3552
    num_examples: 5
  download_size: 53050
  dataset_size: 49776
- config_name: high_school_physics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 61682
    num_examples: 175
  - name: val
    num_bytes: 7266
    num_examples: 19
  - name: dev
    num_bytes: 2266
    num_examples: 5
  download_size: 66380
  dataset_size: 71214
- config_name: high_school_politics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 83356
    num_examples: 176
  - name: val
    num_bytes: 8909
    num_examples: 19
  - name: dev
    num_bytes: 4730
    num_examples: 5
  download_size: 90214
  dataset_size: 96995
- config_name: ideological_and_moral_cultivation
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 35315
    num_examples: 172
  - name: val
    num_bytes: 3241
    num_examples: 19
  - name: dev
    num_bytes: 1296
    num_examples: 5
  download_size: 41532
  dataset_size: 39852
- config_name: law
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 79782
    num_examples: 221
  - name: val
    num_bytes: 8119
    num_examples: 24
  - name: dev
    num_bytes: 4142
    num_examples: 5
  download_size: 83562
  dataset_size: 92043
- config_name: legal_professional
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 121985
    num_examples: 215
  - name: val
    num_bytes: 12215
    num_examples: 23
  - name: dev
    num_bytes: 6974
    num_examples: 5
  download_size: 125081
  dataset_size: 141174
- config_name: logic
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 144246
    num_examples: 204
  - name: val
    num_bytes: 15561
    num_examples: 22
  - name: dev
    num_bytes: 5641
    num_examples: 5
  download_size: 141258
  dataset_size: 165448
- config_name: mao_zedong_thought
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 56699
    num_examples: 219
  - name: val
    num_bytes: 5487
    num_examples: 24
  - name: dev
    num_bytes: 3349
    num_examples: 5
  download_size: 57281
  dataset_size: 65535
- config_name: marxism
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 38662
    num_examples: 179
  - name: val
    num_bytes: 4251
    num_examples: 19
  - name: dev
    num_bytes: 2142
    num_examples: 5
  download_size: 45030
  dataset_size: 45055
- config_name: metrology_engineer
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 47484
    num_examples: 219
  - name: val
    num_bytes: 6116
    num_examples: 24
  - name: dev
    num_bytes: 2485
    num_examples: 5
  download_size: 55033
  dataset_size: 56085
- config_name: middle_school_biology
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 47264
    num_examples: 192
  - name: val
    num_bytes: 5263
    num_examples: 21
  - name: dev
    num_bytes: 4327
    num_examples: 5
  download_size: 58872
  dataset_size: 56854
- config_name: middle_school_chemistry
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 47575
    num_examples: 185
  - name: val
    num_bytes: 5654
    num_examples: 20
  - name: dev
    num_bytes: 3866
    num_examples: 5
  download_size: 59005
  dataset_size: 57095
- config_name: middle_school_geography
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 23329
    num_examples: 108
  - name: val
    num_bytes: 2641
    num_examples: 12
  - name: dev
    num_bytes: 2148
    num_examples: 5
  download_size: 37528
  dataset_size: 28118
- config_name: middle_school_history
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 47076
    num_examples: 207
  - name: val
    num_bytes: 5990
    num_examples: 22
  - name: dev
    num_bytes: 2014
    num_examples: 5
  download_size: 55763
  dataset_size: 55080
- config_name: middle_school_mathematics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 33142
    num_examples: 177
  - name: val
    num_bytes: 4897
    num_examples: 19
  - name: dev
    num_bytes: 3187
    num_examples: 5
  download_size: 45790
  dataset_size: 41226
- config_name: middle_school_physics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 48793
    num_examples: 178
  - name: val
    num_bytes: 5279
    num_examples: 19
  - name: dev
    num_bytes: 3531
    num_examples: 5
  download_size: 60336
  dataset_size: 57603
- config_name: middle_school_politics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 72478
    num_examples: 193
  - name: val
    num_bytes: 7320
    num_examples: 21
  - name: dev
    num_bytes: 3687
    num_examples: 5
  download_size: 75631
  dataset_size: 83485
- config_name: modern_chinese_history
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 51247
    num_examples: 212
  - name: val
    num_bytes: 5188
    num_examples: 23
  - name: dev
    num_bytes: 2983
    num_examples: 5
  download_size: 58881
  dataset_size: 59418
- config_name: operating_system
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 31146
    num_examples: 179
  - name: val
    num_bytes: 3299
    num_examples: 19
  - name: dev
    num_bytes: 2557
    num_examples: 5
  download_size: 39873
  dataset_size: 37002
- config_name: physician
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 89801
    num_examples: 443
  - name: val
    num_bytes: 8710
    num_examples: 49
  - name: dev
    num_bytes: 2033
    num_examples: 5
  download_size: 91373
  dataset_size: 100544
- config_name: plant_protection
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 31877
    num_examples: 199
  - name: val
    num_bytes: 3634
    num_examples: 22
  - name: dev
    num_bytes: 3726
    num_examples: 5
  download_size: 42730
  dataset_size: 39237
- config_name: probability_and_statistics
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 56749
    num_examples: 166
  - name: val
    num_bytes: 5781
    num_examples: 18
  - name: dev
    num_bytes: 6769
    num_examples: 5
  download_size: 62933
  dataset_size: 69299
- config_name: professional_tour_guide
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 41231
    num_examples: 266
  - name: val
    num_bytes: 4509
    num_examples: 29
  - name: dev
    num_bytes: 1764
    num_examples: 5
  download_size: 51538
  dataset_size: 47504
- config_name: sports_science
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 32527
    num_examples: 180
  - name: val
    num_bytes: 3493
    num_examples: 19
  - name: dev
    num_bytes: 4182
    num_examples: 5
  download_size: 44846
  dataset_size: 40202
- config_name: tax_accountant
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 174482
    num_examples: 443
  - name: val
    num_bytes: 18932
    num_examples: 49
  - name: dev
    num_bytes: 4274
    num_examples: 5
  download_size: 147810
  dataset_size: 197688
- config_name: teacher_qualification
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 107369
    num_examples: 399
  - name: val
    num_bytes: 12220
    num_examples: 44
  - name: dev
    num_bytes: 3215
    num_examples: 5
  download_size: 105490
  dataset_size: 122804
- config_name: urban_and_rural_planner
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 110377
    num_examples: 418
  - name: val
    num_bytes: 12793
    num_examples: 46
  - name: dev
    num_bytes: 3166
    num_examples: 5
  download_size: 100220
  dataset_size: 126336
- config_name: veterinary_medicine
  features:
  - name: id
    dtype: int32
  - name: question
    dtype: string
  - name: A
    dtype: string
  - name: B
    dtype: string
  - name: C
    dtype: string
  - name: D
    dtype: string
  - name: answer
    dtype: string
  - name: explanation
    dtype: string
  splits:
  - name: test
    num_bytes: 39465
    num_examples: 210
  - name: val
    num_bytes: 4559
    num_examples: 23
  - name: dev
    num_bytes: 2362
    num_examples: 5
  download_size: 48398
  dataset_size: 46386
---

C-Eval is a comprehensive Chinese evaluation suite for foundation models. It consists of 13948 multi-choice questions spanning 52 diverse disciplines and four difficulty levels. Please visit our [website](https://cevalbenchmark.com/) and [GitHub](https://github.com/SJTU-LIT/ceval/tree/main) or check our [paper](https://arxiv.org/abs/2305.08322) for more details.

Each subject consists of three splits: dev, val, and test.  The dev set per subject consists of five exemplars with explanations for few-shot evaluation. The val set is intended to be used for hyperparameter tuning. And the test set is for model evaluation. Labels on the test split are not released, users are required to submit their results to automatically obtain test accuracy. [How to submit?](https://github.com/SJTU-LIT/ceval/tree/main#how-to-submit)

### Load the data
```python
from datasets import load_dataset
dataset=load_dataset(r"ceval/ceval-exam",name="computer_network")

print(dataset['val'][0])
# {'id': 0, 'question': '使用位填充方法，以01111110为位首flag，数据为011011111111111111110010，求问传送时要添加几个0____', 'A': '1', 'B': '2', 'C': '3', 'D': '4', 'answer': 'C', 'explanation': ''}
```
More details on loading and using the data are at our [github page](https://github.com/SJTU-LIT/ceval#data).

Please cite our paper if you use our dataset.
```
@article{huang2023ceval,
title={C-Eval: A Multi-Level Multi-Discipline Chinese Evaluation Suite for Foundation Models}, 
author={Huang, Yuzhen and Bai, Yuzhuo and Zhu, Zhihao and Zhang, Junlei and Zhang, Jinghan and Su, Tangjun and Liu, Junteng and Lv, Chuancheng and Zhang, Yikai and Lei, Jiayi and Fu, Yao and Sun, Maosong and He, Junxian},
journal={arXiv preprint arXiv:2305.08322},
year={2023}
}
```


