# Task 1 — Getting Onboarded to Nautilus

**Devansh Patil · CMPM 118 (AIEA Lab auditor) · Project: Self-Explainable Deep Neural Networks**

**Setup.** Nautilus is the National Research Platform's Kubernetes cluster; auditors work in the `aiea-auditors` namespace. I installed `kubectl` and `kubelogin`, downloaded the cluster config from nrp.ai into `~/.kube/config`, and logged in through CILogon. Then I asked Leilani to add me to the namespace. Before that, `kubectl auth can-i list pods -n aiea-auditors` returned *no*; afterwards it returned *yes*, and I could create Jobs.

**Login problem.** Choosing *University of California, Santa Cruz* on CILogon failed with "Permission denied – authenticate with the source you've previously signed up with." My NRP account had been created earlier with **ORCID**, and NRP rejects a different identity provider for the same email. Logging in with ORCID fixed it.

**First job.** I ran a Kubernetes **Job** rather than a Deployment, because it runs to completion and exits instead of staying up. That suits a one-off run and avoids leaving idle resources, which the lab warns about. It requested 4 CPU and 8 Gi RAM (requests = limits, no GPU, since this is inference only) plus a 2 Gi PVC to cache the dataset. The job clones the SENN reference code (`KRLGroup/memory-wrap`), downloads SVHN, evaluates the pre-trained Memory Wrap model and generates memory-image explanations.

```bash
kubectl apply -n aiea-auditors -f senn-pvc.yaml
kubectl apply -n aiea-auditors -f senn-job.yaml
kubectl logs  -n aiea-auditors -f job/dvpatil-senn-task4
kubectl cp    aiea-auditors/<pod>:/results ./nautilus-results
kubectl delete -n aiea-auditors job/dvpatil-senn-task4 configmap/senn-scripts pvc/dvpatil-senn
```

**What happened.** The first run crashed with `ModuleNotFoundError: No module named 'utils'`. My helper script ran the code with `runpy`, which doesn't add the script's folder to Python's import path. `kubectl logs` showed the exact error; I fixed the script, updated the ConfigMap and re-ran, and the dataset cached on the PVC let it skip the download. The second run reached **80.37%** test accuracy (same as on my laptop) in **10.2 minutes**, versus about 26 minutes locally, and produced 20 figures, which I copied out with `kubectl cp`. Then I deleted the Job, ConfigMap and PVC.

**What I learned.** Use a Job for work that finishes; size requests to real usage (mine used about 1.3 of 4 cores, so 2 would have been enough); read `kubectl logs` first when something fails; and clean up as soon as you have your results.
