# /usr/bin/env python3.6
# -*- mode: python -*-
# =============================================================================
#  @@-COPYRIGHT-START-@@
#
#  Copyright (c) 2022, Qualcomm Innovation Center, Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#
#  SPDX-License-Identifier: BSD-3-Clause
#
#  @@-COPYRIGHT-END-@@
# =============================================================================
# pylint: skip-file
""" QuantSim and QAT code example to be used for documentation generation. """

# Quantsim imports

import logging
import torch
import torch.cuda
from torch.utils.data import DataLoader
from torchvision import models
from aimet_common.utils import AimetLogger
from aimet_common.defs import QuantScheme
from aimet_torch.utils import create_fake_data_loader
from aimet_torch.model_preparer import prepare_model
from aimet_torch.quantsim import QuantizationSimModel

# End of import statements


def pass_calibration_data(sim_model):
    """
    The User of the QuantizationSimModel API is expected to write this function based on their data set.
    This is not a working function and is provided only as a guideline.

    :param sim_model:
    :return:
    """

    # User action required
    # The following line of code is an example of how to use the ImageNet data's validation data loader.
    # Replace the following line with your own dataset's validation data loader.
    data_loader = ImageNetDataPipeline.get_val_dataloader()

    # User action required
    # For computing the activation encodings, around 1000 unlabelled data samples are required.
    # Edit the following 2 lines based on your batch size.
    # batch_size * max_batch_counter should be 1024
    batch_size = 64
    max_batch_counter = 16

    sim_model.eval()

    current_batch_counter = 0
    with torch.no_grad():
        for input_data, target_data in data_loader:

            inputs_batch = input_data  # labels are ignored
            sim_model(inputs_batch)

            current_batch_counter += 1
            if current_batch_counter == max_batch_counter:
                break


def quantize_and_finetune_example():

    AimetLogger.set_level_for_all_areas(logging.INFO)
    model = models.resnet18().eval()
    model.cuda()
    input_shape = (1, 3, 224, 224)
    dummy_input = torch.randn(input_shape).cuda()

    # Prepare the model for Quantization Simulation. This will automate some changes required in model definition.
    # For example, create modules for torch.nn.functional and create unique modules for reused modules.
    prepared_model = prepare_model(model)

    # Instantiate Quantization Simulation Model. This will insert simulation nodes in the model
    quant_sim = QuantizationSimModel(prepared_model, dummy_input=dummy_input,
                                     quant_scheme=QuantScheme.post_training_tf_enhanced,
                                     default_param_bw=8, default_output_bw=8,
                                     config_file='../../TrainingExtensions/common/src/python/aimet_common/quantsim_config/'
                                                 'default_config.json')

    # Compute encodings(min, max, delta, offset, scale) for activations and parameters.
    # Use around 1000 representative sample from your dataset.
    quant_sim.compute_encodings(pass_calibration_data, forward_pass_callback_args=None)

    # Quantization Aware Training - Fine-tune the model for  few epochs to retain accuracy using your pipeline's train()

    # User action required
    # The following line of code illustrates that the model is getting finetuned.
    # Replace the following train() function with your pipeline's train() function.
    train(quant_sim.model)

    # Export the model which saves pytorch model without any simulation nodes and saves encodings file for both
    # activations and parameters in JSON format
    quant_sim.export(path='./', filename_prefix='quantized_resnet18', dummy_input=dummy_input.cpu())


if __name__ == '__main__':
    quantize_and_finetune_example()
