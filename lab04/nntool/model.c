#include <stdint.h>
#include <stdio.h>
#include "AutoTilerLib.h"
#include "CNN_Generators_SQ8.h"

#include "CNN_Copy_Generators.h"





void model_lab4Model(unsigned int L1Memory, unsigned int L2Memory, unsigned int L3Memory, unsigned int L3Flash)
{
    KernelOper_T Cop = KOP_CONV;

    // SetKernelOpts(KER_OPT_NONE, KER_OPT_BUFFER_PROMOTE);
    SetSymbolDynamics();

    SetUsedFilesNames(0, 3, "Gap.h", "model_lab4.h", "CNN_BasicKernels_SQ8.h");
    SetGeneratedFilesNames("model_lab4Kernels.c", "model_lab4Kernels.h");


    SetMemoryDeviceInfos(4,
        AT_MEM_L1, L1Memory, "model_lab4_L1_Memory", 0, 0,
        AT_MEM_L2, L2Memory, "model_lab4_L2_Memory", 0, 1,
        AT_MEM_L3_HRAM, L3Memory, "model_lab4_L3_Memory", 0, 0,
        AT_MEM_L3_HFLASH, L3Flash, "model_lab4_L3_Flash", "model_lab4_L3_Flash_Const.dat", 0
    );

    LoadCNN_SQ8_Library();


    
    // generator for input_1_formatter
    CNN_Norm("S1_Op_input_1_formatter", 32, 32, 1, KOP_NORM_RGB888);
    
    // generator for _conv1_Conv_fusion
    CNN_ConvolutionPoolAct_SQ8("S4_Conv2d_6x3x5x5_MaxPool_2x2_Relu", 0,
                               4, 1,
                               3, 6, 32, 32,
                               KOP_CONV, 5, 5, 1, 1, 1, 1, 0,
                               KOP_MAXPOOL, 2, 2, 1, 1, 2, 2, 0,
                               KOP_RELUM);
    
    // generator for _conv2_Conv_fusion
    CNN_ConvolutionPoolAct_SQ8("S7_Conv2d_16x6x5x5_MaxPool_2x2_Relu", 0,
                               4, 1,
                               6, 16, 14, 14,
                               KOP_CONV, 5, 5, 1, 1, 1, 1, 0,
                               KOP_MAXPOOL, 2, 2, 1, 1, 2, 2, 0,
                               KOP_RELUM);
    
    // generator for _fc1_MatMul_fusion
    CNN_LinearAct_SQ8("S10_Op__fc1_MatMul_fusion", 0,
                      4, 1,
                      400, 120,
                      KOP_LINEAR, KOP_RELUM);
    
    // generator for _fc2_MatMul_fusion
    CNN_LinearAct_SQ8("S13_Op__fc2_MatMul_fusion", 0,
                      4, 1,
                      120, 84,
                      KOP_LINEAR, KOP_RELUM);
    
    // generator for _fc3_MatMul
    CNN_LinearAct_SQ8("S16_Linear_10x84", 0,
                      4, 1,
                      84, 10,
                      KOP_LINEAR, KOP_NONE);
    

#define GRAPH
#ifdef GRAPH
    CreateGraph("model_lab4CNN",
        /* Arguments either passed or globals */
            CArgs(27,
                TCArgInfo("unsigned char * __restrict__", "Input_1", ARG_SCOPE_ARG, ARG_DIR_IN, AT_MEM_L2, AT_MEM_L2, 0),
                TCArgInfo("signed char * __restrict__", "_conv1_conv_weights", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/_conv1_conv_weights.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed int * __restrict__", "_conv1_conv_biases", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/_conv1_conv_biases.tensor", 1, 1, 32, 0)),
                TCArgInfo("unsigned char * __restrict__", "S4_Mul_scale", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S4_Mul_scale.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed char * __restrict__", "S4_Mul_shift", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S4_Mul_shift.tensor", 1, 1, 8, 0)),
                // in: 0.01661 out: 0.01661  actscale: [1] actscalen: [0] a0: [-128] b0: 0 c0: 0 BIASN: 0 PRENORM: 0
                TCArgInfo("signed char * __restrict__", "S4_Infos", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S4_Infos.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed char * __restrict__", "_conv2_conv_weights", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/_conv2_conv_weights.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed int * __restrict__", "_conv2_conv_biases", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/_conv2_conv_biases.tensor", 1, 1, 32, 0)),
                TCArgInfo("unsigned char * __restrict__", "S7_Mul_scale", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S7_Mul_scale.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed char * __restrict__", "S7_Mul_shift", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S7_Mul_shift.tensor", 1, 1, 8, 0)),
                // in: 0.02188 out: 0.02188  actscale: [1] actscalen: [0] a0: [-128] b0: 0 c0: 0 BIASN: 0 PRENORM: 0
                TCArgInfo("signed char * __restrict__", "S7_Infos", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S7_Infos.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed char * __restrict__", "_fc1_matmul_weights", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/_fc1_matmul_weights.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed int * __restrict__", "_fc1_matmul_biases", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/_fc1_matmul_biases.tensor", 1, 1, 32, 0)),
                TCArgInfo("unsigned char * __restrict__", "S10_Mul_scale", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S10_Mul_scale.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed char * __restrict__", "S10_Mul_shift", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S10_Mul_shift.tensor", 1, 1, 8, 0)),
                // in: 0.02618 out: 0.02618  actscale: [1] actscalen: [0] a0: [-128] b0: 0 c0: 0 BIASN: 0 PRENORM: 0
                TCArgInfo("signed char * __restrict__", "S10_Infos", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S10_Infos.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed char * __restrict__", "_fc2_matmul_weights", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/_fc2_matmul_weights.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed int * __restrict__", "_fc2_matmul_biases", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/_fc2_matmul_biases.tensor", 1, 1, 32, 0)),
                TCArgInfo("unsigned char * __restrict__", "S13_Mul_scale", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S13_Mul_scale.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed char * __restrict__", "S13_Mul_shift", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S13_Mul_shift.tensor", 1, 1, 8, 0)),
                // in: 0.01284 out: 0.01284  actscale: [1] actscalen: [0] a0: [-128] b0: 0 c0: 0 BIASN: 0 PRENORM: 0
                TCArgInfo("signed char * __restrict__", "S13_Infos", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S13_Infos.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed char * __restrict__", "_fc3_matmul_weights", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/_fc3_matmul_weights.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed int * __restrict__", "_fc3_matmul_biases", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/_fc3_matmul_biases.tensor", 1, 1, 32, 0)),
                TCArgInfo("unsigned char * __restrict__", "S16_Mul_scale", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S16_Mul_scale.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed char * __restrict__", "S16_Mul_shift", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S16_Mul_shift.tensor", 1, 1, 8, 0)),
                // no activation BIASN: 0 PRENORM: 0
                TCArgInfo("signed char * __restrict__", "S16_Infos", ARG_SCOPE_GLOBAL, ARG_DIR_CONSTIN, AT_MEM_L3_HFLASH, AT_MEM_UNDEF, ConstInfo("tensors/S16_Infos.tensor", 1, 1, 8, 0)),
                TCArgInfo("signed char * __restrict__", "Output_1", ARG_SCOPE_ARG, ARG_DIR_OUT, AT_MEM_L2, AT_MEM_L2, 0)
            ),
        /* Locals, allocated dynamically */
        CArgs(5,
            TCArgInfo("signed char * __restrict__", "S1_Output", ARG_SCOPE_LOCAL, ARG_DIR_INOUT, AT_MEM_UNDEF, AT_MEM_UNDEF, 0),
            TCArgInfo("signed char * __restrict__", "S4_Output", ARG_SCOPE_LOCAL, ARG_DIR_INOUT, AT_MEM_UNDEF, AT_MEM_UNDEF, 0),
            TCArgInfo("signed char * __restrict__", "S7_Output", ARG_SCOPE_LOCAL, ARG_DIR_INOUT, AT_MEM_UNDEF, AT_MEM_UNDEF, 0),
            TCArgInfo("signed char * __restrict__", "S10_Output", ARG_SCOPE_LOCAL, ARG_DIR_INOUT, AT_MEM_UNDEF, AT_MEM_UNDEF, 0),
            TCArgInfo("signed char * __restrict__", "S13_Output", ARG_SCOPE_LOCAL, ARG_DIR_INOUT, AT_MEM_UNDEF, AT_MEM_UNDEF, 0)
        )
    );

    /* Stacked tensors - Concats */
    // no concats in graph so not stacked tensors created

    // Node input_1_formatter inq 0.00<(u8-0.00)*1.00000000<255.00 outq 0.00<(i8--128.00)*0.00392157<1.00
    AddNode("S1_Op_input_1_formatter",
        Bindings(2,
            GNodeArg(GNA_IN, "Input_1", 0),
            GNodeArg(GNA_OUT, "S1_Output", 0)
        )
    );
    // Node S4_Conv2d_6x3x5x5_MaxPool_2x2_Relu inq 0.00<(i8--128.00)*0.00392157<1.00 weightsq chan<(i8-0.00)*chan<chan outq 0.00<(i8--128.00)*0.01660956<4.24 biasesq chan<(i32-0.00)*chan<chan
    AddNode("S4_Conv2d_6x3x5x5_MaxPool_2x2_Relu",
        Bindings(7,
            GNodeArg(GNA_IN, "S1_Output", 0),
            GNodeArg(GNA_IN, "_conv1_conv_weights", 0),
            GNodeArg(GNA_IN, "_conv1_conv_biases", 0),
            GNodeArg(GNA_OUT, "S4_Output", 0),
            GNodeArg(GNA_IN, "S4_Mul_scale", 0),
            GNodeArg(GNA_IN, "S4_Mul_shift", 0),
            GNodeArg(GNA_IN, "S4_Infos", 0)
        )
    );
    // Node S7_Conv2d_16x6x5x5_MaxPool_2x2_Relu inq 0.00<(i8--128.00)*0.01660956<4.24 weightsq chan<(i8-0.00)*chan<chan outq 0.00<(i8--128.00)*0.02187510<5.58 biasesq chan<(i32-0.00)*chan<chan
    AddNode("S7_Conv2d_16x6x5x5_MaxPool_2x2_Relu",
        Bindings(7,
            GNodeArg(GNA_IN, "S4_Output", 0),
            GNodeArg(GNA_IN, "_conv2_conv_weights", 0),
            GNodeArg(GNA_IN, "_conv2_conv_biases", 0),
            GNodeArg(GNA_OUT, "S7_Output", 0),
            GNodeArg(GNA_IN, "S7_Mul_scale", 0),
            GNodeArg(GNA_IN, "S7_Mul_shift", 0),
            GNodeArg(GNA_IN, "S7_Infos", 0)
        )
    );
    // Node _fc1_MatMul inq 0.00<(i8--128.00)*0.02187510<5.58 weightsq chan<(i8-0.00)*chan<chan outq 0.00<(i8--128.00)*0.02618133<6.68
    AddNode("S10_Op__fc1_MatMul_fusion",
        Bindings(7,
            GNodeArg(GNA_IN, "S7_Output", 0),
            GNodeArg(GNA_IN, "_fc1_matmul_weights", 0),
            GNodeArg(GNA_IN, "_fc1_matmul_biases", 0),
            GNodeArg(GNA_OUT, "S10_Output", 0),
            GNodeArg(GNA_IN, "S10_Mul_scale", 0),
            GNodeArg(GNA_IN, "S10_Mul_shift", 0),
            GNodeArg(GNA_IN, "S10_Infos", 0)
        )
    );
    // Node _fc2_MatMul inq 0.00<(i8--128.00)*0.02618133<6.68 weightsq chan<(i8-0.00)*chan<chan outq 0.00<(i8--128.00)*0.01283977<3.27
    AddNode("S13_Op__fc2_MatMul_fusion",
        Bindings(7,
            GNodeArg(GNA_IN, "S10_Output", 0),
            GNodeArg(GNA_IN, "_fc2_matmul_weights", 0),
            GNodeArg(GNA_IN, "_fc2_matmul_biases", 0),
            GNodeArg(GNA_OUT, "S13_Output", 0),
            GNodeArg(GNA_IN, "S13_Mul_scale", 0),
            GNodeArg(GNA_IN, "S13_Mul_shift", 0),
            GNodeArg(GNA_IN, "S13_Infos", 0)
        )
    );
    // Node _fc3_MatMul inq 0.00<(i8--128.00)*0.01283977<3.27 weightsq chan<(i8-0.00)*chan<chan outq -4.48<(i8-0.00)*0.03497572<4.44 forced
    AddNode("S16_Linear_10x84",
        Bindings(7,
            GNodeArg(GNA_IN, "S13_Output", 0),
            GNodeArg(GNA_IN, "_fc3_matmul_weights", 0),
            GNodeArg(GNA_IN, "_fc3_matmul_biases", 0),
            GNodeArg(GNA_OUT, "Output_1", 0),
            GNodeArg(GNA_IN, "S16_Mul_scale", 0),
            GNodeArg(GNA_IN, "S16_Mul_shift", 0),
            GNodeArg(GNA_IN, "S16_Infos", 0)
        )
    );
    CloseGraph();
#endif
}

int main(int argc, char **argv)

{
    if (TilerParseOptions(argc, argv)) {
            printf("Failed to initialize or incorrect output arguments directory.\n"); return 1;
    }
    model_lab4Model(64000, 300000, 8000000, 64*1024*1024);
    GenerateTilingCode();
    return 0;
}
