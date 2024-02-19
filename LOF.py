import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt

class LOF:
    def __init__(self):
        pass
    
    def euclidean_distance(self, x1, x2):
        return torch.sqrt(torch.sum((x1 - x2) ** 2, dim=1))

    def k_distance(self, k, x, distances):
        sorted_distances, _ = torch.sort(distances, dim=0)
        return sorted_distances[k]

    def reachability_distance(self, k, x_i, x_j, distances):
        return torch.max(self.k_distance(k, x_j, distances), self.euclidean_distance(x_i, x_j))

    def local_reachability_density(self, k, x_i, neighbors, distances):
        sum_reachability = torch.sum(self.reachability_distance(k, x_i, neighbors, distances))
        return len(neighbors) / sum_reachability

    def local_outlier_factor(self, k, x, distances):
        n = x.size(0)
        lof = torch.zeros(n)
        for i in range(n):
            neighbors = torch.cat([x[:i], x[i+1:]], dim=0)
            lrd_i = self.local_reachability_density(k, x[i], neighbors, distances[i])
            lrd_neighbors = torch.stack([self.local_reachability_density(k, x[j], neighbors, distances[j]) for j in range(n) if j != i])
            lof[i] = torch.mean(lrd_neighbors) / lrd_i
        return lof

# 사용 예시:
lof_instance = LOF()

# 랜덤 데이터 생성
torch.manual_seed(42)
num_samples = 100
num_features = 2
data = torch.randn(num_samples, num_features)

# 모든 쌍의 거리 계산
distances = torch.cdist(data, data)

# k 값 선택 (가장 가까운 이웃의 수)
k = 5

# LOF 점수 계산
lof_scores = lof_instance.local_outlier_factor(k, data, distances)
# 데이터 시각화
plt.figure(figsize=(10, 6))
plt.scatter(data[:, 0], data[:, 1], c=lof_scores, cmap='viridis')
plt.colorbar(label='LOF 점수')
plt.title('LOF 점수에 따른 데이터 시각화')
plt.xlabel('특성 1')
plt.ylabel('특성 2')
plt.show()
