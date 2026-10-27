# Task 5 — Paper Summary: Memory Wrap

**Devansh Patil · CMPM 118 (AIEA Lab auditor) · Project: Self-Explainable Deep Neural Networks (SENN)**

**Paper:** B. La Rosa, R. Capobianco, D. Nardi. *A self-interpretable module for deep image classification on small data* (Applied Intelligence, 2022). Preprint title: *Memory Wrap: a Data-Efficient and Interpretable Extension to Image Classification Models* (arXiv:2106.01440).

## The problem

Deep image classifiers have two weaknesses that keep them out of high-stakes settings. They need a lot of labelled data, and they are black boxes: they give an answer but no reason for it. Research on few-shot learning tackles the first problem and explainable AI (XAI) tackles the second, but few methods address both at once. The paper asks whether one small change to a network can make it learn better from little data *and* explain its own predictions.

## The idea

Normally a network uses the training set only to set its weights and then throws it away. Memory Wrap keeps some of it around. At every step it draws a random **memory set** of 100 training images (about 10 per class) and passes them through the network together with the input. The idea comes from Memory Augmented Neural Networks (Neural Turing Machines, Differentiable Neural Computers).

Memory Wrap replaces only the **last layer** of an existing classifier, so it works with any architecture. The rest of the model (ResNet18, MobileNet-v2, EfficientNet, etc.) becomes an **encoder** that turns each image into a feature vector. Then:

1. The input and every memory image are encoded.
2. The **cosine similarity** between the input encoding and each memory encoding is computed and passed through **sparsemax** instead of softmax. Sparsemax sets most weights to exactly zero, so only a handful of memory images get a say.
3. Those weights are used to build a **memory vector**: a weighted sum of the memory encodings.
4. The memory vector is concatenated with the input encoding and fed to a small MLP (one hidden layer) that outputs the class.

The memory vector adds features from similar, already-labelled examples that may be weak or missing in the input itself. That is why it helps most when training data is scarce.

## How it explains itself

Because the prediction is built directly from a few weighted memory images, those images *are* the explanation; no separate explainer is needed. The authors split the memory set into three groups:

- **Explanations by example** (positive weight, predicted as the same class as the input): "this looks like these."
- **Counterfactuals** (positive weight, but predicted as a different class): similar images the model considered but rejected. They show what the model was "doubting."
- **Ignored samples** (weight exactly zero): no influence on the decision.

Looking at which samples got positive weight reveals what the model focuses on. In one SVHN example, shifting the image slightly changes the used memories from 5s and 3s to 1s and 7s, which suggests the network looks at the shape of the centred digit. In another, the top memories share the *background colour* but not the digit, revealing that the model was using a wrong shortcut. The authors also apply Integrated Gradients (via the Captum library) to the input and its top memory images to produce pixel heatmaps.

## Experiments and results

They tested MobileNet-v2, ResNet18, EfficientNet-B0 and others on **SVHN, CIFAR10 and CINIC10**, training on reduced subsets of 1,000, 2,000 and 5,000 images as well as the full datasets. Every configuration was run 15 times with fixed seeds. They compared against the unmodified network ("Standard") and an "Only Memory" variant that drops the input encoding from the final layer.

- **Low-data accuracy:** Memory Wrap beats the standard model everywhere, sometimes by a lot. MobileNet-v2 on 1,000 SVHN images goes from **42.7% to 66.9%**, and on 2,000 images from **70.9% to 81.4%**. Gains are largest on SVHN and with MobileNet, and smallest with ResNet18.
- **Stability:** standard networks vary a lot between runs on small data (ResNet18 on 2,000 SVHN images: ±18%), while Memory Wrap's spread is much smaller.
- **Full datasets:** accuracy is about the same as the standard model, so you get the interpretability without losing performance.
- **Explanations are faithful:** if the highest-weighted memory image is fed back into the model, it is predicted as the same class as the original input about 91% of the time (MobileNet-v2, SVHN, 2,000 images). So the weight ranking reflects what the model actually uses.
- **Built-in uncertainty signal:** when the top-weighted memory is a *counterfactual*, accuracy drops to about 40–50%. This happens on roughly 10% of test images and could be used to warn a user that a prediction is unreliable.

## Limitations

- **Cost:** every step also encodes 100 memory images, which roughly doubles training time. MobileNet-v2 grows from 2.3M to 15.4M parameters because of the larger final MLP.
- **Bias amplification:** because the memory is chosen by similarity, it can reinforce shortcuts the encoder has already learned (like the background-colour example). The method makes this easy to *spot* but has no fix for it yet.
- **Random memory sets:** the memory is sampled randomly and shared across a whole batch, so results depend somewhat on which samples were drawn (the authors average 5 test passes to compensate).
- The Integrated Gradients heatmaps depend on the chosen baseline image (white), which makes them blind to white regions.

## Connection to my project

The SENN auditor project builds directly on this paper. In Task 2 I loaded the authors' pre-trained Memory Wrap MobileNet-v2 (trained on 2,000 SVHN images) and generated "memory images" for test digits: each figure shows the input, the predicted class, and the memory samples with positive weight. In the next tasks I will look specifically at the model's **wrong predictions**, inspect their memory images, and test whether choosing a different memory set can correct them. That idea follows naturally from this paper: if the memory drives the prediction, changing the memory should change the answer.
