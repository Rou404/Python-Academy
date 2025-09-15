# Run all pattern demos in order.
import creational.singleton_demo as s
import creational.factory_method_demo as f
import structural.adapter_demo as a
import structural.decorator_demo as d
import behavioral.strategy_demo as st
import behavioral.observer_demo as o

if __name__ == "__main__":
    s.demo()
    f.demo()
    a.demo()
    d.demo()
    st.demo()
    o.demo()
