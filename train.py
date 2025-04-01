import torch
import torch.nn as nn
import torch.optim as optim
import time

# Check if CUDA is available; if not, fallback to CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[Train Script] Using device: {device}")

# --------------------------------------------------------
# 1) Create a small dummy dataset
#    Let's say 1000 samples, each with 20 features,
#    and a binary label (0 or 1).
# --------------------------------------------------------
num_samples = 1000
num_features = 20
X = torch.randn(num_samples, num_features)  # Random data
y = torch.randint(0, 2, (num_samples,))     # 0 or 1 labels

# Move data to the device (GPU or CPU)
X = X.to(device)
y = y.to(device)

# --------------------------------------------------------
# 2) Define a simple neural network
#    For instance, a small feed-forward model.
# --------------------------------------------------------
class SimpleNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

model = SimpleNet(input_size=num_features, hidden_size=32, num_classes=2)
model = model.to(device)

# --------------------------------------------------------
# 3) Define loss function and optimizer
# --------------------------------------------------------
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# --------------------------------------------------------
# 4) Training loop
# --------------------------------------------------------
num_epochs = 5

print("[Train Script] Starting training...")
start_time = time.time()

for epoch in range(num_epochs):
    # Forward pass
    outputs = model(X)
    loss = criterion(outputs, y)

    # Backward pass and optimization
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

total_time = time.time() - start_time
print(f"[Train Script] Training finished in {total_time:.2f} seconds.")

# --------------------------------------------------------
# 5) Test how well the model does on the dummy data
# --------------------------------------------------------
with torch.no_grad():
    outputs = model(X)
    _, predicted = torch.max(outputs, 1)
    accuracy = (predicted == y).float().mean()
    print(f"[Train Script] Training accuracy on dummy data: {accuracy * 100:.2f}%")
