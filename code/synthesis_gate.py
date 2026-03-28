import torch
import numpy as np
import matplotlib.pyplot as plt
import torch.nn.functional as F

# --- 1. ENGINE CONSTANTS ---
B_LOW, B_HIGH = 5.0, 7.0
S_LOW, S_HIGH = 5.0, 9.0
GRID_SIZE = 200
device = torch.device("cpu")
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23]

# Pure, Stable Propagation Kernel
kernel = torch.ones((1, 1, 3, 3, 3), device=device).float()
kernel[0, 0, 1, 1, 1] = 0

print("Poole Manifold Research | Trial 242: The Synthesis Gate (0 + 1 + 0)...")

def run_manifold(f, inhibitor_mask, threshold_mask, amplifier_mask):
    with torch.no_grad():
        f_float = f.float()
        padded = F.pad(f_float, (1, 1, 1, 1, 1, 1), mode='circular')
        potential = F.conv3d(padded, kernel, padding=0)

        # Thermodynamics
        potential[inhibitor_mask] -= 15.0
        potential[threshold_mask] -= 2.0
        potential[amplifier_mask] += 1.0

        resonance = torch.zeros_like(potential)
        for p in PRIMES:
            resonance += 0.35 * torch.exp(-((potential - p)**2) / 0.01)

        total_phi = potential + resonance

    birth = (f == 0) & (total_phi >= B_LOW) & (total_phi <= B_HIGH)
    survive = (f == 1) & (total_phi >= S_LOW) & (total_phi <= S_HIGH)

    return (birth | survive).float()

# ==========================================
# CLASS: THE SYNTHESIS POOLE FULL-ADDER
# ==========================================
class PooleFullAdder:
    def __init__(self, origin_y, origin_x, z_mid):
        self.oy = origin_y
        self.ox = origin_x
        self.z = z_mid

    def stamp(self, inh, thr, amp):
        oy, ox, z = self.oy, self.ox, self.z

        # 1. MAIN PLUMBING PIPES (Wide Open Highways)
        inh[0, 0, oy-3:oy+3, ox-40:ox-4, z-2:z+2] = False # Input A
        inh[0, 0, oy-40:oy-4, ox-3:ox+3, z-2:z+2] = False # Input B
        inh[0, 0, oy-3:oy+3, ox+4:ox+140, z-2:z+2] = False # Sum 1
        inh[0, 0, oy-4:oy+4, ox-4:ox+4, z-2:z+2] = False # Hollow Intersection

        # ==========================================
        # 2. HA1: THE SYNTHESIS ARCHITECTURE
        # ==========================================

        # COMPONENT 1: THE COLD WALL (Guards Input A)
        thr[0, 0, oy-3:oy+3, ox-8:ox-4, z-2:z+2] = True # -2.0 Drag Sponge
        amp[0, 0, oy-3:oy+3, ox-16:ox-8, z-2:z+2] = True # +1.0 Injector to help A later

        # COMPONENT 2: THE GEOMETRIC CHAMFER (Deflects B's downward inertia)
        inh[0, 0, oy:oy+4, ox-3:ox-2, z-2:z+2] = True
        inh[0, 0, oy+1:oy+4, ox-2:ox-1, z-2:z+2] = True
        inh[0, 0, oy+2:oy+4, ox-1:ox, z-2:z+2] = True
        inh[0, 0, oy+3:oy+4, ox:ox+1, z-2:z+2] = True

        # COMPONENT 3: THE CONCRETE PINHOLE (Guards the Carry Diagonal)
        for i in range(40):
            inh[0, 0, oy+4+i-3:oy+4+i+3, ox+4+i-3:ox+4+i+3, z-2:z+2] = False

        # The -15.0 Solid Concrete Seal
        inh[0, 0, oy+3:oy+9, ox+3:ox+9, z-2:z+2] = True
        # The 2-unit wide Void Pinhole (0+1 ignores it, 1+1 blows it open)
        inh[0, 0, oy+5:oy+7, ox+5:ox+7, z-2:z+2] = False

        # COMPONENT 4: THE THERMAL RIVER (Pulls fluid smoothly to Sum 1)
        amp[0, 0, oy-3:oy+3, ox+4:ox+20, z-2:z+2] = True

        # (Cin Vertical Track)
        inh[0, 0, oy-40:oy+140, ox+97:ox+103, z-2:z+2] = False

        # ==========================================
        # 3. DOWNSTREAM LOGIC (Isolated Check Valve)
        # ==========================================
        inh[0, 0, oy-3:oy-1, ox+50:ox+52, z-2:z+2] = True
        inh[0, 0, oy+1:oy+3, ox+50:ox+52, z-2:z+2] = True
        thr[0, 0, oy-1:oy+1, ox+50:ox+52, z-2:z+2] = True
        amp[0, 0, oy-2:oy+2, ox+45:ox+49, z-2:z+2] = True
        amp[0, 0, oy-2:oy+2, ox+70:ox+75, z-2:z+2] = True

        # CIN DELAY LINE & DEFIBRILLATOR
        inh[0, 0, oy+55:oy+65, ox+97:ox+103, z-2:z+2] = True
        inh[0, 0, oy+60:oy+66, ox+97:ox+112, z-2:z+2] = False
        inh[0, 0, oy+54:oy+66, ox+106:ox+112, z-2:z+2] = False
        inh[0, 0, oy+54:oy+60, ox+97:ox+112, z-2:z+2] = False
        amp[0, 0, oy+45:oy+47, ox+98:ox+102, z-2:z+2] = True

        # HA2: SECOND HALF-ADDER
        amp[0, 0, oy-8:oy-4, ox+98:ox+102, z-2:z+2] = True
        amp[0, 0, oy-2:oy+2, ox+104:ox+108, z-2:z+2] = True

        inh[0, 0, oy-3:oy-1, ox+105:ox+115, z-2:z+2] = True
        inh[0, 0, oy+1:oy+3, ox+105:ox+115, z-2:z+2] = True
        inh[0, 0, oy-15:oy-5, ox+97:ox+99, z-2:z+2] = True
        inh[0, 0, oy-15:oy-5, ox+101:ox+103, z-2:z+2] = True
        for i in range(40):
            inh[0, 0, oy-i-3:oy-i+3, ox+100+i-3:ox+100+i+3, z-2:z+2] = False

# --- 2. INITIALIZATION ---
torch.manual_seed(137)
field = torch.zeros((1, 1, GRID_SIZE, GRID_SIZE, GRID_SIZE), device=device)
z_mid = GRID_SIZE // 2

inhibitor_mask = torch.ones_like(field).bool()
threshold_mask = torch.zeros_like(field).bool()
amplifier_mask = torch.zeros_like(field).bool()

# Stamp the Microchip
adder = PooleFullAdder(origin_y=50, origin_x=50, z_mid=z_mid)
adder.stamp(inhibitor_mask, threshold_mask, amplifier_mask)

# ==========================================
# FIRING THE LOGIC: 0 + 1 + 0 = 01
# ==========================================
# Fire Input B (Top) ONLY
field[0, 0, 12:15, 49:51, z_mid-1:z_mid+1] = 1.0

history = []
print("Executing Synthesis Gate Test: 0 + 1 + 0...")
for t in range(401):
    field = run_manifold(field, inhibitor_mask, threshold_mask, amplifier_mask)

    # --- SYNTHESIS TELEMETRY SYSTEM (GEN 250) ---
    if t == 250:
        print("\n--- GEN 250 SYNTHESIS TELEMETRY ---")
        sum1_mass = int(field[0, 0, 45:55, 65:80, z_mid].sum().item())
        carry1_leakage = int(field[0, 0, 55:70, 55:70, z_mid].sum().item())
        input_a_backflow = int(field[0, 0, 45:55, 20:40, z_mid].sum().item())

        print(f"Sum 1 Channel Kinetic Mass: {sum1_mass}")
        print(f"Carry Pinhole Leakage: {carry1_leakage}")
        print(f"Input A Leftward Backsplash: {input_a_backflow}")

        if carry1_leakage == 0 and input_a_backflow == 0 and sum1_mass > 0:
            print("Status: FLAWLESS LOGIC GATE - All physics perfectly balanced.")
        else:
            print("Status: CONTAINMENT BREACH.")
        print("----------------------------------\n")

    if t % 100 == 0:
        history.append(field[0, 0, :, :, z_mid].clone().numpy())

# --- 3. VISUALIZATION ---
num_frames = len(history)
fig, axes = plt.subplots(1, num_frames, figsize=(6*num_frames, 6), facecolor='black')
for i, data in enumerate(history):
    axes[i].imshow(data, cmap='inferno')
    axes[i].set_title(f"Gen {i*100}", color='white')
    axes[i].axis('off')
plt.show()
