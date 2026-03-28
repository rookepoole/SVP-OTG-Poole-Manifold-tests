# =============================================================================
# WEAK LENSING CONVERGENCE POWER SPECTRUM — Poole Manifold
# =============================================================================

import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt

device = torch.device("cpu")
GRID_SIZE = 128
LAMBDA_P = 0.10
SIGMA_P = 0.3568

kernel = torch.ones((1, 1, 3, 3, 3), device=device).float()
kernel[0, 0, 1, 1, 1] = 0

def run_poole(f):
    with torch.no_grad():
        padded = F.pad(f.float(), (1,1,1,1,1,1), mode='circular')
        neigh = F.conv3d(padded, kernel, padding=0)
        birth = (f == 0) & (neigh >= 5) & (neigh <= 7)
        survive = (f == 1) & (neigh >= 5) & (neigh <= 9)
        return (birth | survive).float()

# Stabilize (if needed)
torch.manual_seed(137)
field = (torch.rand((1,1,GRID_SIZE,GRID_SIZE,GRID_SIZE), device=device) > 0.5).float()
for t in range(600):
    field = run_poole(field)

density = field[0,0].cpu().numpy().astype(float)
print(f"Stabilized density: {density.mean():.4f}")

# Simple projected convergence (line-of-sight integral along z)
kappa = density.sum(axis=2) / GRID_SIZE   # normalized projection

# Compute 2D angular power spectrum proxy
fft2 = np.fft.fft2(kappa)
power = np.abs(fft2)**2
power = np.fft.fftshift(power)

# Radial binning for C_ℓ proxy
y, x = np.indices(power.shape)
center = np.array([GRID_SIZE//2, GRID_SIZE//2])
r = np.sqrt((x - center[1])**2 + (y - center[0])**2).astype(int)
tbin = np.bincount(r.ravel(), power.ravel())
nr = np.bincount(r.ravel())
radial_profile = tbin / nr
ell = np.arange(len(radial_profile))

# Plot
plt.figure(figsize=(9, 6))
plt.plot(ell[:80], radial_profile[:80], 'o-', color='purple', label='Poole κ C_ℓ proxy')
plt.xlabel('Multipole ℓ (proxy)')
plt.ylabel('C_ℓ (arbitrary units)')
plt.title('Weak Lensing Convergence Power Spectrum — Throughput Drag Field')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

print("Weak lensing convergence power spectrum computed.")
