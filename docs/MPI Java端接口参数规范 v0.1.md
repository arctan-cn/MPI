# MPI Java端接口参数规范 v0.1

## 初期参数规范

| 请求类型 | 功能描述 | 参数列表 | 返回值 |
| ------- | ------- | ------- | ------- |
| `login` | 验证接口密码 | `password:str` | 无 |
| `disconnect` | 断开socket连接 | `null` | 状态码700 |
| `command` | 发送Minecraft命令 | `command:str` | 命令返回值 |
| `execute` | 代替实体执行命令 | `(target) command:str` | 命令返回值 |
| `selector` | 通过选择器选择实体 | `selector:str` | 实体JSON |
| `print` | 输出字符串到屏幕 | `target:[(target) \| "@a"] rawtext:str` | 无 |

## 后期添加参数规范

| 请求类型 | 功能描述 | 参数列表 | 返回值 |
| ------- | ------- | ------- | ------- |
| `registerCommand` | 注册自定义命令 | `namespace:str name:str handle:str` | 无 |
| `registerEvent` | 注册自定义事件 | `eventName:str customName:str` | 实体JSON |
| `bindEventListener` | 注册事件监听器 | `event:str handle:str` | 无 |

## 注释

* [1] `(target)` 表示参数 `selector:str\|entities:array`
* [2] `[...A / ...B]` 表示当未传入A参数或A参数无值时，默认A参数的值为B
