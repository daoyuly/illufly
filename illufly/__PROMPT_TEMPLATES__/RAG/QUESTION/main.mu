你是强大的AI助手，可以帮我构造问题检索的例子，请帮我：

1、设想一个{{last_input}}的问题描述
2、根据该问题扩散成{{count}}个该问题的不同问法，形成提问角度清单
3、为了增强扩散检索的效果，尽量不要出现明显相同的关键字，
4、先根据原始问题和新增的提问角度清单构造{{count}}个相关问答对
5、再构造{{count}}个无关问答对，这些问答应当与原始问题和提问角度清单都没有直接相似性不容易从文本相似检索得到
6、请不要评论，不要解释，不要废话
7、直接使用下面的格式输出，并注意不要修改 @xxx 标签位置和名称：

```markdown
@metadata tag='related'
**Question:**
 (强相关的问法1)

**Answer:**
(针对问法1的回答)

@metadata tag='related'
**Question:**
 (强相关的问法2)

**Answer:**
(针对问法2的回答)

...(一共包括{{count}}个抢相关问答对)

@metadata tag='unrelated'
**Question:**
 (无关的问法3)

**Answer:**
(针对问法3的回答)

@metadata tag='unrelated'
**Question:**
 (无关的问法4)

**Answer:**
(针对问法4的回答)

...(一共包括{{count}}个无关问答对)

```