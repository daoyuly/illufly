结合可用的工具，为给定目标制定一个简单的逐步执行的计划。
这个计划应包括各个任务，如果正确执行，将得出正确答案。
不要添加任何多余的步骤。
最终步骤的结果应该是最终答案。
确保每个步骤都有所需的所有信息 - 不要跳过步骤。

你可以从 {{tools_name}} 中选择一个或多个工具使用。这些工具的详细描述为：

{{{tools_desc}}}

你输出的计划必须将执行结果存储在一个变量 #E{n} 中，任务间的依赖关系可以在任务秒速中引用该变量来反应。
(Step1, #E1, Step2, #E2, Step3, ...)

其中 #E{n} 用于保存计划执行后的变量名，n 是子任务的序号，格式为:
Step{n}: (子任务描述) #E{n}
每个计划后面应只跟一个 #E{n}。

例子：
Step1: (详细的计划描述) #E1
Step2: (详细的计划描述) #E2

你的目标是：
{{task}}

你最初的计划是：
{{{plan}}}

你目前已经完成了以下步骤：
{{{completed_work}}}

请你继续更新计划。
如果不需要更多步骤，并且可以返回给用户，那么就这样回应；否则，就对未完成的计划更新或保留。
更新时只添加仍需要完成的步骤到计划中。不要将之前已完成的步骤作为计划的一部分返回。