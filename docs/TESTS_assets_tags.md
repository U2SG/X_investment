# 资产标签批量操作自动化测试用例说明

本文件整理了 test_assets_tags.py 中所有自动化测试用例，涵盖资产批量添加/移除标签API的核心功能、边界场景、安全校验、幂等性、异常处理等。

---

## 1. 基础功能与正向用例

- **test_batch_add_tags_to_assets**
  - 目的：验证批量为多个资产添加标签的基本功能。
  - 场景：创建两个资产，分别批量添加多个标签，断言标签正确关联。

- **test_batch_remove_tags_from_assets**
  - 目的：验证批量为多个资产移除标签的基本功能。
  - 场景：批量移除部分标签，断言剩余标签正确。

- **test_batch_add_and_remove_tags_with_auth**
  - 目的：验证登录用户可正常批量添加和移除标签。
  - 场景：模拟登录，添加后移除部分标签，断言剩余标签。

---

## 2. 权限与认证

- **test_batch_add_tags_requires_auth_detail**
  - 目的：未登录用户访问批量添加标签API时应返回401。
  - 场景：不带token请求，断言401和标准错误信息。

- **test_batch_remove_tags_requires_auth_detail**
  - 目的：未登录用户访问批量移除标签API时应返回401。
  - 场景：不带token请求，断言401和标准错误信息。

---

## 3. 参数校验与异常

- **test_batch_add_tags_invalid_tags_field**
  - 目的：tags为空列表或全为空字符串时应返回400。
  - 场景：非法tags参数，断言400。

- **test_batch_remove_tags_invalid_tags_field**
  - 目的：tags为空列表或全为空字符串时应返回400。
  - 场景：非法tags参数，断言400。

- **test_batch_add_tags_param_validation**
  - 目的：asset_id非法、tags非法时应返回400。
  - 场景：asset_id为0、非int，tags为[]、空字符串、非str，断言400。

- **test_batch_remove_tags_param_validation**
  - 目的：asset_id非法、tags非法时应返回400。
  - 场景：同上。

---

## 4. 边界与幂等性

- **test_batch_add_tags_empty_request**
  - 目的：空请求体时应返回空结果。
  - 场景：json=[]，断言返回[]。

- **test_batch_remove_tags_empty_request**
  - 目的：空请求体时应返回空结果。
  - 场景：json=[]，断言返回[]。

- **test_batch_add_tags_idempotent**
  - 目的：同一资产多次出现时，结果与合并后等价。
  - 场景：多次添加不同标签，断言标签集合。

- **test_batch_remove_tags_idempotent**
  - 目的：同一资产多次出现时，移除标签幂等。
  - 场景：多次移除不同标签，断言标签为空。

- **test_batch_add_tags_duplicate_tag_names_in_tags_list**
  - 目的：tags列表中同一标签重复出现时自动去重。
  - 场景：添加["A", "A", "B"]，断言结果为{"A", "B"}。

- **test_batch_remove_tags_duplicate_tag_names_in_tags_list**
  - 目的：移除时tags列表重复，结果与去重后等价。
  - 场景：移除["A", "A", "B"]，断言标签为空。

---

## 5. 容错与健壮性

- **test_batch_add_tags_with_nonexistent_tag**
  - 目的：部分标签名不存在时自动创建。
  - 场景：添加新标签和已存在标签，断言都被关联。

- **test_batch_remove_tags_with_nonexistent_tag**
  - 目的：移除不存在的标签不会报错。
  - 场景：移除部分存在、部分不存在的标签，断言剩余标签。

- **test_batch_add_tags_with_nonexistent_asset**
  - 目的：部分asset_id不存在时，其他合法项能正常处理。
  - 场景：合法和不存在的asset_id混合，断言只返回合法资产结果。

- **test_batch_remove_tags_with_nonexistent_asset**
  - 目的：移除时部分asset_id不存在，其他合法项能正常处理。
  - 场景：合法和不存在的asset_id混合，断言只返回合法资产结果。

---

## 6. 标签引用计数与自动清理

- **test_shared_tag_ref_count_and_auto_delete**
  - 目的：同一标签被多个资产共享时，移除部分资产的标签后引用计数正确，全部移除后自动删除。
  - 场景：两个资产共享标签，逐步移除，断言引用计数和标签存在性。

- **test_shared_tag_ref_count_and_auto_delete_v2**
  - 目的：同上，冗余测试，覆盖不同资产和标签名。

---

## 7. 其他

- **register_and_login**
  - 辅助函数：注册并登录用户，返回token。

---

> 本文档仅覆盖 test_assets_tags.py，建议后续为其他API和测试用例也补充类似说明文档。 