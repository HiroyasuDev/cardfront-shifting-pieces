using System;
using System.Collections.Generic;

namespace Synapse.TcgEngine.Tools
{
    /// <summary>
    /// Clean-room deterministic event & effect resolution scheduler.
    /// In AI lookahead mode (instantMode = true), all queued actions resolve synchronously with zero delay.
    /// In client presentation mode (instantMode = false), queued steps can pause for VFX/animation durations.
    /// </summary>
    public sealed class SynapseResolveQueue
    {
        public sealed class QueuedStep
        {
            public string stepKind;
            public string sourceCardUid;
            public string targetCardUid;
            public int targetX;
            public int targetY;
            public Action executeCallback;

            public void Reset()
            {
                stepKind = null;
                sourceCardUid = null;
                targetCardUid = null;
                targetX = -1;
                targetY = -1;
                executeCallback = null;
            }
        }

        private readonly SynapsePool<QueuedStep> _pool = new SynapsePool<QueuedStep>();
        private readonly Queue<QueuedStep> _queue = new Queue<QueuedStep>();
        private readonly bool _instantMode;
        private float _remainingDelay;
        private bool _isResolving;

        public SynapseResolveQueue(bool instantMode = false)
        {
            _instantMode = instantMode;
        }

        public bool IsBusy => _isResolving || _queue.Count > 0 || _remainingDelay > 0f;
        public int PendingCount => _queue.Count;

        public void EnqueueStep(string stepKind, Action callback, string sourceUid = null, string targetUid = null, int x = -1, int y = -1)
        {
            if (callback == null) return;
            var step = _pool.Rent();
            step.stepKind = stepKind;
            step.sourceCardUid = sourceUid;
            step.targetCardUid = targetUid;
            step.targetX = x;
            step.targetY = y;
            step.executeCallback = callback;
            _queue.Enqueue(step);
        }

        public void SetDelay(float seconds)
        {
            if (!_instantMode && seconds > _remainingDelay)
            {
                _remainingDelay = seconds;
            }
        }

        public void Tick(float deltaTime)
        {
            if (_remainingDelay > 0f)
            {
                _remainingDelay -= deltaTime;
                if (_remainingDelay <= 0f)
                {
                    DrainAll();
                }
            }
            else if (_queue.Count > 0)
            {
                DrainAll();
            }
        }

        public void DrainAll()
        {
            if (_isResolving) return;
            _isResolving = true;
            try
            {
                while (_queue.Count > 0)
                {
                    if (!_instantMode && _remainingDelay > 0f) break;
                    var step = _queue.Dequeue();
                    var cb = step.executeCallback;
                    step.Reset();
                    _pool.Return(step);
                    cb?.Invoke();
                }
            }
            finally
            {
                _isResolving = false;
            }
        }

        public void Clear()
        {
            while (_queue.Count > 0)
            {
                var s = _queue.Dequeue();
                s.Reset();
                _pool.Return(s);
            }
            _pool.ReturnAll();
            _remainingDelay = 0f;
            _isResolving = false;
        }
    }
}
