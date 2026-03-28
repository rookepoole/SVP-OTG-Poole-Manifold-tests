# =============================================================================
# FULL THROUGHPUT DRAG RSD MULTIPOLES — ξ₀(s) and ξ₂(s)
# =============================================================================

import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fftn, ifftn, fftfreq

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

# Stabilize grid
torch.manual_seed(137)
field = (torch.rand((1,1,GRID_SIZE,GRID_SIZE,GRID_SIZE), device=device) > 0.5).float()
for t in range(600):
    field = run_poole(field)

density = field[0,0].cpu().numpy().astype(np.float64)
drag = np.clip((density - LAMBDA_P) / SIGMA_P, 0.0, 1.0)

print(f"Stabilized density: {density.mean():.4f}")

# Throughput Drag-weighted field (LOS along z)
los_weighted = density * drag

# FFT → power spectrum
fft3d = fftn(los_weighted)
power3d = np.abs(fft3d)**2

# k and μ (LOS = z)
kfreq = fftfreq(GRID_SIZE, d=1.0/GRID_SIZE)
kx, ky, kz = np.meshgrid(kfreq, kfreq, kfreq, indexing='ij')
k_mag = np.sqrt(kx**2 + ky**2 + kz**2 + 1e-12)
mu = kz / k_mag

# Legendre moments in Fourier space
P0 = power3d.mean()
P2 = (5.0/2.0) * np.mean((3*mu**2 - 1) * power3d)

# Inverse FFT to get real-space correlation multipoles
xi0 = np.real(ifftn(power3d))
xi2 = np.real(ifftn((3*mu**2 - 1) * power3d)) * (5.0/2.0)

# Radial binning for plots
s_max = GRID_SIZE // 2
s_bins = np.arange(0, s_max + 1)
s_centers = (s_bins[:-1] + s_bins[1:]) / 2.0

# Flatten and bin
r = np.arange(len(xi0.flatten()))
hist0, _ = np.histogram(r, bins=s_bins, weights=xi0.flatten())
counts, _ = np.histogram(r, bins=s_bins)
xi0_binned = hist0 / counts

hist2, _ = np.histogram(r, bins=s_bins, weights=xi2.flatten())
xi2_binned = hist2 / counts

# Plot ξ₀(s)
plt.figure(figsize=(9, 5))
plt.plot(s_centers, xi0_binned, 'o-', color='blue', label='ξ₀(s) — Monopole')
plt.axhline(0, color='gray', linestyle='--')
plt.xlabel('s (lattice units)')
plt.ylabel('ξ(s)')
plt.title('Throughput Drag RSD — Monopole ξ₀(s)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

# Plot ξ₂(s)
plt.figure(figsize=(9, 5))
plt.plot(s_centers, xi2_binned, 'o-', color='red', label='ξ₂(s) — Quadrupole')
plt.axhline(0, color='gray', linestyle='--')
plt.xlabel('s (lattice units)')
plt.ylabel('ξ(s)')
plt.title('Throughput Drag RSD — Quadrupole ξ₂(s)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()

print("Full ξ₀(s) and ξ₂(s) multipoles computed.")
print(f"Monopole proxy P0: {P0:.2e}")
print(f"Quadrupole proxy P2: {P2:.2e}")
