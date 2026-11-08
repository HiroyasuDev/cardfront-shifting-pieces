using System;
using System.Collections.Generic;

namespace Synapse.TcgEngine.Tools
{
    /// <summary>
    /// Clean-room proprietary zero-allocation object pool for deterministic AI lookahead and resolve queues.
    /// </summary>
    public sealed class SynapsePool<T> where T : new()
    {
        private readonly Stack<T> _free = new Stack<T>();
        private readonly HashSet<T> _active = new HashSet<T>();

        public T Rent()
        {
            T item = _free.Count > 0 ? _free.Pop() : new T();
            _active.Add(item);
            return item;
        }

        public void Return(T item)
        {
            if (item != null && _active.Remove(item))
            {
                _free.Push(item);
            }
        }

        public void ReturnAll()
        {
            foreach (var item in _active)
            {
                _free.Push(item);
            }
            _active.Clear();
        }

        public int ActiveCount => _active.Count;
        public int FreeCount => _free.Count;
    }

    /// <summary>
    /// Clean-room scratchpad list pair that eliminates GC allocations during target filtering.
    /// </summary>
    public sealed class SwapBuffer<T>
    {
        public readonly List<T> Primary = new List<T>(16);
        public readonly List<T> Secondary = new List<T>(16);

        public List<T> GetClearedPrimary()
        {
            Primary.Clear();
            return Primary;
        }

        public List<T> GetClearedSecondary()
        {
            Secondary.Clear();
            return Secondary;
        }
    }
}
