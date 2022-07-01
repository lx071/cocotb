# 简要说明
## Cocotb的使用方式
Cocotb的使用方式其实和使用Verilog编写Testbench方式无异,在Verilog的Testbench中，整个`testbench.v`文件都运行在仿真器中，通过我们给DUT不断输入时钟和相关的输入，观察DUT的内部状态来确定是否符合我们的设计预期。这里以一个加法器的例子，作为DUT进行说明。
```
module adder(
input clk,
input reset,
input [7:0]a,
input [7:0]b,

output reg[7:0]c
    ); 
 
 always@(posedge clk)begin
   if(reset)
     c <= 0;
   else
     c <= a + b;
 end
    
endmodule

```
以下为使用Verilog编写的Testbench:
```
module tb();
//Inputs
reg clk;
reg reset;
reg [7:0] a;
reg [7:0] b;
//Outputs
wire [7:0] c;
//Instantiate the Design Under Test(DUT)
adder dut(
  .clk(clk),
  .reset(reset),
  .a(a),
  .b(b),
  .c(c)
);
initial begin
  //Initialize Inputs
  clk = 0;
  reset = 0;
  a = 0;
  b = 0;
  #10;
  reset = 1;
  #10;
  reset = 0;
  #100;
  a = 4;
  b = 7;
  #10;
  a = 8;
  b = 17;
  // Add stimulus here
  
end
  always #5 clk = ~clk
endmodule
```
而使用Cocotb进行硬件测试其实也是一样的套路：通过时钟生成器不断给clk输入，进行复位操作、进行初始化、给相关输入端口激励。只不过DUT和以上的操作不在同一层，DUT在仿真器中，以上的操作在Python环境中，是利用协程来模拟出如等待N个时钟周期、等待时钟上升沿/下降沿等相关操作。以下为使用Cocotb编写的Testbench：
```python
async def clkgen(dut):
    while True:
        await Timer(5, "NS")
        dut.clk <= 1
        await Timer(5, "NS")
        dut.clk <= 0
        
       
async def reset(dut):
    await Timer(10, "NS")
    dut.reset <= 0
    for i in range(10):
        await RisingEdge(dut.clk)
    dut.reset <= 1
    
    
@cocotb.test()
async def test(dut):
    clkgen = cocotb.fork(clkgen(dut))
    reset = cocotb.fork(reset(dut))
    dut.a = 0
    dut.b = 0
    await Timer(100, "NS")
    dut.a = 4
    dut.b = 7
    await Timer(10, "NS")
    dut.a = 8
    dut.b = 17

```
因此，和硬件交互的操作其实不多，只有赋值/取值，等待N个周期，等待时钟沿，其中想要并行运行就用fork。其他的高级特性操作就根据你对Python的熟悉程度来使用
## 所谓使用BFM的Cocotb
其实所谓的BFM的Cocotb的背景前提是，在使用Cocotb进行硬件测试时，可以发现，每个clk他都要进行一次赋值的，而由于赋值操作他需要和仿真器进行通信，不同于Verilog编写的Testbench是和仿真器处于同一进程。所以一定程度上会减慢仿真运行效率。

所以一种方案是，减少和仿真器交流频次。如何能减少呢？其实就是把Driver（负责赋值的功能模块，也可以叫BFM）作为一个Verilog模块和DUT连接在一起作为一个新的DUT，其中BFM负责将获取的数值通过解析后，每个时钟对原来的DUT进行赋值。因此主要的关键是如何实现和Verilog模块的通信，将数值（如32位的整数）传输到BFM中。
### DPI/VPI接口
其实通信的关键就是使用DPI/VPI接口，其中DPI接口是System Verilog的特性，而DPI接口的最终实现会利用到VPI接口，这里的相关实现原理和介绍，请通过谷歌查找相关英文文档。这里主要以`DPI`接口进行说明

对于具有C环境和Verilog环境的两个文件，想要实现两个环境间的通信，最简单的方法就是使用DPI接口。DPI接口的使用方式很简单，只需要进行声明后，然后利用具有gcc编译器的仿真器对他进行编译即可直接调用。

想要调用C文件的函数的话，需要在SV文件中使用import "DPI-C"声明，且要声明好函数名、返回类型、传入参数类型
```
import "DPI-C" function void cfunc(logic in);
```
想要在C文件中调用SV的任务或函数，需要在SV文件中使用export "DPI-C"声明，且C文件也要声明
```
in SV
export "DPI-C" function svfunc;

in c
extern "C" void svfunc(svLogic);
```
这里简化了很多说明，最主要的是C和SV之间数据类型的对应关系，如sv中logic类型，在c中用什么来表示

### BFM的Cocotb
虽然说利用DPI/VPI接口实现了C和SV之间的通信，但是这里是使用Cocotb，也就是说`需要实现Python环境和C环境之间的调用，也就是说需要实现Python中的函数可以直接调用C中实现的函数`

正是因为需要实现多次语言间的切换，如果按照上述的方式使用，需要对使用的函数进行编译后，然后Python通过共享文件库找到对应的方法，才能在Python种调用C中的函数，这种方式太蠢，牺牲了代码编写的方便性，提高了些许的运行效率。因此，实现了所谓的`BFM管理器`
#### BFM管理器
BFM管理器的作用是能识别每一个BFM（使用C++实现），通过将每个BFM使用ID进行管理和识别后，他可以为BFM文件自动生成相关声明（利用ID命名方法名，而不是手动命名）

由于BFM管理器对BFM进行了管理，只需一套代码，可以进行任何BFM与C文件之间的调用，因此在Python中，只需实现Python环境调用C++中的方法即可。

#### 文件结构
+ cocotb/bfms.py: 在Python环境的BFM的实现
+ cocotb/bfmgen.py: 自动生成DPI/VPI声明的模版
+ cocotb/decorators.py: 486行后，装饰器实现。用于声明哪些方法需要被SV文件调用；哪些方法需要由SV文件实现，在Python中调用SV中的方法/函数
+ cocotb/share：有些是新增加的文件，如GPIBfm.cpp：BFM管理器的实现；有些修改了一些源代码，如simulatormodule.c, 用于在Python中可以调用C代码的函数；还修改了仿真器的makefile文件，让仿真前需要编译自动生成c文件、.v文件，由于比较杂，具体请参考git的修改记录

## 使用方式，以最简单的握手为例子
### Verilog的BFM
+ tests/test_case/test_bfms_verilog/rv_bfms/hdl中

第一要点：
Verilog的BFM实现需要根据具体实现逻辑实现，例如在简单握手协议的BFM中，需要有输出信号Valid，输入信号Ready，只有当两个信号为高时，表示握手成功，此时才能进行具体操作。

因此，什么时候需要让Valid信号为高，且此时传递什么数据，应该由Python用户端来决定，所以需要在此写个任务，供Python端来调用该任务：
```
task write_req(reg[63:0] d);
		begin
			data_v = d;
			data_valid_v = 1;
		end
endtask
```
当握手成功后，需要与Python端同步，告诉此时是握手成功的，所以在握手成功时调用了一个函数`write_ack();`,这个函数应该由Python端实现
```
if (data_valid && data_ready) 
    begin
		write_ack();

		if (!data_valid_v) 
		    begin
		        data_valid <= 0;
			end
	end
```
第二要点： 需要添加声明关键字，由于实现了BFM管理器，他会根据具体ID来自动实现，所以只需添加符号
`${cocotb_bfm_api_impl}` 就会生成相关API
### Python版本的BFM
+ tests/test_case/test_bfms_verilog/rv_bfms中

Python版本的BFM里面没有具体的时序代码（也就是通过句柄dut来访问信号），他的作用是作为BFM对象，让用户可以通过该对象来调用Verilog模块中的任务/函数，或者让Verilog中调用Python中的函数

第一要点：
需要在类的头上使用装饰器,用于指定Verilog/SV的BFM在哪里
```python
@cocotb.bfm(hdl={
    cocotb.bfm_vlog : cocotb.bfm_hdl_path(__file__, "hdl/rv_data_out_bfm.v"),
    cocotb.bfm_sv   : cocotb.bfm_hdl_path(__file__, "hdl/rv_data_out_bfm.v")
    })
```

第二要点：
需要在跨环境的函数上使用装饰器,需要调用SV中的任务或函数时，使用bfm_import；需要由SV中调用Python的函数时，使用bfm_export;

对于SV中实现的任务/函数，则在Python端他是没有内容的，直接添加pass即可。如果该方法需要传递参数，需要在装饰器上指定参数类型，如这里指定write_req传递的参数类型为32位整数

使用export装饰器装饰的函数，表明需要在Python中实现
```python
    @cocotb.bfm_import(cocotb.bfm_uint32_t)
    def write_req(self, d):
        pass

    @cocotb.bfm_export()
    def write_ack(self):
        self.ack_ev.set()
```
第三要点：
write_c函数才是给用户调用的函数，虽然不是直接赋值给DUT，但是还需要进行Python和仿真器环境的信息同步，所以用到了事件和锁机制，在开始尝试进行握手时，需要尝试获取锁，并在Verilog 的BFM完成握手时，告知Python，并将锁释放。
```python
    @cocotb.coroutine
    def write_c(self, data):
        '''
        Writes the specified data word to the interface
        '''

        yield self.busy.acquire()
        self.write_req(data)

        # Wait for acknowledge of the transfer
        yield self.ack_ev.wait()
        self.ack_ev.clear()

        self.busy.release()
```
### Testbench
+ bfm_test.py文件

这里和使用Cocotb基本无异，只是在使用时，需要找到BFM对象,这里的".*u_dut"是根据在Verilog文件中实例化的名字决定的

然后通过bfm对象，即可像操作对象一样进行赋值操作。
```python
        bfm = cocotb.BfmMgr.find_bfm(".*u_dut")

```
```
rv_data_out_bfm #(32) u_dut (
			.clock(clock),
			.reset(reset),
			.data(data),
			.data_valid(data_valid),
			.data_ready(data_ready)
		);

	rv_data_monitor_bfm #(32) u_mon (
			.clock(clock),
			.reset(reset),
			.data(data),
			.data_valid(data_valid),
			.data_ready(data_ready)
		);

```
# 说明
目前这个所谓的BFM的Cocotb，只能运行于1.3版本，迁移到1.4版本以上，需要又要非常了解Cocotb的项目结构和代码才可以。
