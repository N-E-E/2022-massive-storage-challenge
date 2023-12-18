[简体中文](./README-zh.md)

original url: https://gitee.com/N_E_E/huawei_storage_cup

### Update
11.7 Value Function Method Completed

11.8 Insight: Time Delay, Set Minimum Time, Only Process if Remaining Implementation Time is Below the Threshold (Effective, 226)

### Usage

```bash
cd src
python Demo.py
```

### Current Optimization Directions
- Storage Method for Request Information: Heap/Tree/Lazy Deletion/Advanced Data Structures?
- Priority Levels for Processing Various Requests: Urgency, Balancing Bonus/Penalty, Required Driver Space-----Comprehensive Consideration?
- How to Select Requests to Fill Drives to Maximize Utilization at the Current Moment: Binary Search Optimization/Heuristic Algorithm?
- Encapsulate a Scorer for Easy Maintenance in the Future. Haven't implemented penalty for sending requests to the wrong driver yet.

### File Structure

- AlgCore: Contains core scheduling algorithms
  - AlgBase: Abstract base class (do not modify), unifies some API for algorithms (additional functions can be added in the inheriting class)
  - ListSeqAlg: Basic greedy scheduling implementation, relatively poor performance
  - loss_func_method_1: Value function method
  - xxx: Personally implemented algorithms can inherit AlgBase, placed under the AlgCore directory for easy access by Demo and Scheduler
- logs: Output log folder
- Scheduler: Officially provided interface; if implemented by inheriting AlgBase, just change `self.method` to your algorithm class for direct testing
- score: Encapsulated simulated scorer
- logger: Printing/Saving output results for debugging
- Demo: Testing function; if implemented by inheriting AlgBase, no modification is needed.