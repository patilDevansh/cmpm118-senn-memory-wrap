# Task 1 / Task 3 — Getting Onboarded to Nautilus

**Devansh Patil · CMPM 118 (AIEA Lab auditor) · Project: Self-Explainable Deep Neural Networks**

## What Nautilus is

Nautilus is the Kubernetes cluster run by the National Research Platform (NRP, nrp.ai). The AIEA lab uses it for GPU and CPU compute. Auditors work in the `aiea-auditors` namespace. You don't log into a machine; you describe the work in a YAML file (a Pod, Job or Deployment) and `kubectl` asks the cluster to run it.

## Setup steps

1. **Local tools.** Installed `kubectl` and `kubelogin` (`kubectl oidc-login`) with Homebrew, plus Docker.
2. **Config.** Downloaded the cluster config from nrp.ai ("Get Config") into `~/.kube/config`. The context is `nautilus`, which logs in through OIDC.
3. **Logging in.** Ran `kubectl get nodes`, which opens a browser login (a local callback on `localhost:8000`) through CILogon.
4. **Namespace access.** Asked Leilani in #namespace-request (and by DM) to be added to `aiea-auditors`. Before being added, `kubectl auth can-i list pods -n aiea-auditors` returned **no**; afterwards it returned **yes**, and I can also create Jobs.

### Problem: "Permission denied" at login

My first login attempts, choosing *University of California, Santa Cruz* on CILogon, failed with:

> Request to authenticate with CiLogon has been denied. Please authenticate with the source you've previously signed up with.

I had created my NRP account earlier with a different identity provider. NRP links an account to the identity it was created with, and a different provider with the same email is rejected. Logging in with **ORCID**, the provider I originally used, worked. The lab guide's advice is for UCSC students to use the UCSC option; this only matters if you already have an account. `kubectl auth whoami` now shows my CILogon user.

## First job

I ran a Kubernetes **Job**: it runs to completion and exits, unlike a Deployment, which stays up. That suits a one-off run and avoids leaving idle resources, which the lab and NRP both warn about.

- **What it does:** clones the SENN reference code (`KRLGroup/memory-wrap`), downloads the SVHN dataset, evaluates the pre-trained Memory Wrap model and generates memory-image explanations. Details are in the Task 4 report.
- **Resources:** 4 CPU, 8 Gi RAM, no GPU (inference only), with requests equal to limits as NRP requires. Plus a 2 Gi `rook-ceph-block` PersistentVolumeClaim to cache the dataset.
- **Commands:**
  ```bash
  kubectl create configmap senn-scripts -n aiea-auditors --from-file=...   # helper scripts
  kubectl apply -n aiea-auditors -f senn-pvc.yaml
  kubectl apply -n aiea-auditors -f senn-job.yaml
  kubectl logs -n aiea-auditors -f job/dvpatil-senn-task4
  kubectl cp aiea-auditors/<pod>:/results ./nautilus-results
  kubectl delete -n aiea-auditors job/dvpatil-senn-task4 configmap/senn-scripts pvc/dvpatil-senn
  ```

### What happened

- **First attempt failed.** The Job started on `nautilus-it-gpu07.fullerton.edu`, installed everything and downloaded the dataset, then crashed with `ModuleNotFoundError: No module named 'utils'`. `kubectl logs` showed the exact error: my helper script didn't put the repo folder on Python's import path when running inside the container. I fixed the script, updated the ConfigMap and re-applied the Job.
- **Second attempt succeeded.** The model evaluated to **80.37%** test accuracy (same as on my laptop) in **10.2 minutes**, versus about 26 minutes locally, and generated 20 memory-image figures. I copied them out with `kubectl cp`.
- **Cleanup.** I deleted the Job, ConfigMap and PVC immediately afterwards and checked that nothing of mine was left in the namespace.

## What I learned

- A Job is the right object for a run that finishes. Deployments are for services and get flagged if left running.
- Keep `requests` equal to `limits` and size them to what the code actually uses. My job only used about 1.3 of its 4 cores, so next time I'd request 2.
- Clean up everything (Job, ConfigMap, PVC) as soon as you have your results.
- A failed run is cheap to debug: `kubectl logs` showed the exact Python error, I fixed the script, updated the ConfigMap and re-ran. The cached dataset on the PVC meant the second run skipped the download.
