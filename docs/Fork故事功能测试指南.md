# 🧪 Fork 故事功能测试指南

## 🎯 功能说明

Fork 功能允许用户将别人的优秀故事复制到自己的仓库，成为独立的新故事。

### 与协作续写的区别

| 功能 | 协作续写 | Fork 故事 |
|------|----------|-----------|
| 故事关系 | 同一个故事 | 创建新副本 |
| 首页显示 | 只显示1个 | 显示多个独立故事 |
| 作者权限 | 原作者生成视频 | Fork者成为新作者 |
| 内容变化 | 协作添加 | 独立发展 |

---

## 📋 测试场景

### 场景1: Fork 别人的故事

#### 操作步骤：

1. **用户 ssh 创建故事**：
   - 登录昵称：`ssh`
   - 创建故事《中关村》
   - 内容：`这是关于中关村的科技创业故事...`
   - 保存（不生成视频）

2. **用户 Alice 发现并 Fork**：
   - 登录昵称：`Alice`
   - 在首页看到《中关村》（作者：ssh）
   - 点击查看详情
   - 点击"🍴 Fork 到我的仓库"
   - 确认 Fork

#### 预期结果：

- ✅ Fork 成功，跳转到新故事页面
- ✅ 新故事的作者是 `Alice`（不是ssh）
- ✅ 新故事有紫色"🍴 Forked from ssh 的《中关村》"标签
- ✅ Alice 成为这个新故事的"原作者"
- ✅ Alice 可以对这个故事生成视频

---

### 场景2: 首页显示 Fork 的故事

#### 操作步骤：

继续上面的场景，查看首页

#### 预期结果：

**全部故事**:
```
📖 中关村 - ssh · 0/5 人续写
   [查看详情] [续写] [Fork]

🍴 中关村 - Alice · 0/5 人续写
   [查看详情] [续写] [生成视频] ← Alice可见
```

- ✅ 首页显示**两个**《中关村》故事
- ✅ Alice 的故事带有"🍴 Fork"标签
- ✅ 两个故事独立显示

---

### 场景3: "我的故事"筛选

#### 操作步骤：

1. Alice 登录，点击"📁 我的故事"
2. ssh 登录，点击"📁 我的故事"

#### 预期结果：

**Alice 的"我的故事"**:
```
🍴 中关村 - Alice
```

**ssh 的"我的故事"**:
```
中关村 - ssh
```

- ✅ 每个用户只看到自己创建和Fork的故事
- ✅ Alice 看到她Fork的故事
- ✅ ssh 看到他的原创故事

---

### 场景4: Fork 后续写

#### 操作步骤：

1. Alice 在自己Fork的《中关村》上续写
2. 用户 Bob 也在 Alice 的版本上续写

#### 预期结果：

**Alice 的《中关村》详情页**:
```
🍴 Forked from ssh 的《中关村》

中关村
👤 原作者: Alice

📖 Alice 的原创内容
[这是关于中关村的科技创业故事...]

✍️ Bob 的续写 #1
[续写内容...]

📝 续写情况: 1/5 人
```

- ✅ 显示Fork来源
- ✅ Alice 是"原作者"（不是ssh）
- ✅ Bob 可以在 Alice 的版本上续写
- ✅ Alice 可以为自己的版本生成视频

---

### 场景5: Fork 后生成视频

#### 操作步骤：

1. Alice 在自己Fork的《中关村》上点击"🎬 生成视频"
2. ssh 尝试为 Alice 的版本生成视频

#### 预期结果：

- ✅ Alice 可以成功生成视频（她是原作者）
- ✅ ssh **无法**为 Alice 的版本生成视频
- ✅ 视频包含：Alice 的原创内容 + Bob 的续写
- ✅ 两个版本的视频是独立的

---

### 场景6: 不能 Fork 自己的故事

#### 操作步骤：

1. ssh 登录
2. 打开自己创建的《中关村》
3. 尝试点击 Fork 按钮

#### 预期结果：

- ✅ ssh **看不到** Fork 按钮
- ✅ Fork 按钮只对非作者显示

---

### 场景7: 不能重复 Fork

#### 操作步骤：

1. Alice 已经 Fork 了 ssh 的《中关村》
2. Alice 再次尝试 Fork 相同的故事

#### 预期结果：

- ✅ 提示："你已经Fork过这个故事了"
- ✅ 防止重复 Fork

---

### 场景8: Fork 链的显示

#### 操作步骤：

1. Bob Fork Alice 的《中关村》（Alice 的版本是从 ssh Fork的）

#### 预期结果：

**Bob 的《中关村》详情页**:
```
🍴 Forked from Alice 的《中关村》

中关村
👤 原作者: Bob
```

- ✅ 显示直接来源（Alice），不是原始来源（ssh）
- ✅ Bob 成为新作者
- ✅ Bob 可以生成视频

---

### 场景9: 原创故事和 Fork 故事的数据独立

#### 操作步骤：

1. ssh 的原创《中关村》：有3个续写
2. Alice Fork 的《中关村》：有1个续写
3. 查看两个故事的详情页

#### 预期结果：

**ssh 的版本**:
```
中关村 - ssh
📝 续写情况: 3/5 人
[ssh原创 + 续写1 + 续写2 + 续写3]
```

**Alice 的版本**:
```
🍴 中关村 - Alice
📝 续写情况: 1/5 人
[Alice原创(=ssh原创内容) + Bob续写]
```

- ✅ 两个故事的续写数据独立
- ✅ Fork 时复制了原始内容，但后续发展独立
- ✅ 互不影响

---

## 🔍 数据库验证

### 查询原创故事
```sql
SELECT id, title, author, forked_from 
FROM stories 
WHERE parent_id IS NULL;
```

**预期结果**:
```
id=1, title="中关村", author="ssh", forked_from=NULL
id=5, title="中关村", author="Alice", forked_from=1
id=8, title="中关村", author="Bob", forked_from=5
```

### 查询续写关系
```sql
-- ssh 版本的续写
SELECT * FROM stories WHERE parent_id = 1;

-- Alice 版本的续写
SELECT * FROM stories WHERE parent_id = 5;
```

---

## 🎬 完整用户流程

```
T1: ssh 创建《中关村》
    DB: {id:1, author:"ssh", forked_from:NULL}
    首页: [中关村 - ssh]

T2: Alice Fork 到自己仓库
    DB: {id:5, author:"Alice", forked_from:1}
    首页: [中关村 - ssh] + [🍴中关村 - Alice]

T3: Bob 在 Alice 版本上续写
    DB: {id:6, author:"Bob", parent_id:5}
    Alice版本: ssh原创 + Bob续写

T4: Alice 生成视频
    视频内容: ssh原创内容 + Bob续写
    Alice版本: [🎥 有视频]

T5: ssh 的版本仍然独立
    ssh版本: 无视频, 0个续写
    独立发展，互不影响
```

---

## 📊 API 测试

### Fork 故事
```bash
curl -X POST http://localhost:8000/api/stories/1/fork \
  -H "Content-Type: application/json" \
  -d '{"author": "Alice"}'

# 预期返回: 新创建的故事信息（id=5, author="Alice", forked_from=1）
```

### 获取原始信息
```bash
curl http://localhost:8000/api/stories/5/origin

# 预期返回:
{
  "story_id": 5,
  "is_forked": true,
  "origin": {
    "id": 1,
    "title": "中关村",
    "author": "ssh",
    "created_at": "..."
  }
}
```

### 获取"我的故事"
```bash
curl "http://localhost:8000/api/stories?filter_by=my&author=Alice"

# 预期返回: Alice 创建的原创 + Alice Fork 的故事
```

---

## ✅ 验收清单

### 功能完整性
- [ ] 可以 Fork 别人的故事
- [ ] Fork 后创建独立的新故事
- [ ] Fork 者成为新故事的原作者
- [ ] 不能 Fork 自己的故事
- [ ] 不能重复 Fork 同一个故事
- [ ] 首页显示 Fork 标签

### 权限控制
- [ ] Fork 者可以续写自己Fork的故事
- [ ] Fork 者可以为自己Fork的故事生成视频
- [ ] 原作者无法控制Fork后的故事

### UI/UX
- [ ] 显示Fork来源链接
- [ ] "我的故事"正确筛选
- [ ] Fork按钮只对非作者显示
- [ ] Fork成功有明确提示

### 数据独立性
- [ ] Fork故事的续写独立
- [ ] Fork故事的视频独立
- [ ] 互不影响

---

## 🐛 常见问题

### Q1: Fork 按钮对所有人都显示？
**A**: 检查前端条件：`fullStory.original_author !== userNickname`

### Q2: Fork 后还是原作者？
**A**: 检查后端 Fork 接口是否正确设置了 `author` 字段

### Q3: "我的故事"显示不正确？
**A**: 检查 API 是否传递了 `author` 参数：`?filter_by=my&author=Alice`

### Q4: 不能续写 Fork 的故事？
**A**: Fork 后的故事 `parent_id` 应该是 `NULL`，`forked_from` 记录来源

### Q5: Fork 来源显示不出来？
**A**: 检查 `getOriginInfo` API 调用是否成功，`originInfo` 状态是否正确

---

## 🚀 快速测试流程

1. **启动服务**:
   ```bash
   cd /Applications/宋晗搏/黑客松/中关村_22组_hub/Story-Link
   ./start.sh
   ```

2. **打开三个浏览器窗口**:
   - 窗口1: ssh
   - 窗口2（隐身）: Alice
   - 窗口3（隐身）: Bob

3. **测试步骤**:
   - ssh 创建《中关村》
   - Alice Fork 到自己仓库
   - Bob 在 Alice 版本上续写
   - Alice 生成视频
   - 验证ssh版本不受影响

4. **验证点**:
   - 首页显示2个《中关村》
   - Alice版本有Fork标签
   - Alice可以生成视频
   - ssh版本独立发展

---

祝测试顺利！🎉

**功能实现时间**: 2025-10-26  
**测试覆盖**: 9个场景 + API测试

