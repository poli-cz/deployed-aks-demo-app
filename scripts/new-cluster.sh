export LOC=westeurope
export RG=rg-flux-custom
export AKS=aks-flux-custom

# Use your existing ACR if you want:
export ACR_NAME=lakmoosacr
# or create a new ACR:
# export ACR_NAME=lakmoosacr$RANDOM

az group create -n $RG -l $LOC

# If creating new ACR:
# az acr create -g $RG -n $ACR_NAME --sku Basic

az aks create -g $RG -n $AKS -l $LOC \
  --node-count 2 \
  --enable-managed-identity \
  --enable-oidc-issuer \
  --enable-workload-identity \
  --generate-ssh-keys
