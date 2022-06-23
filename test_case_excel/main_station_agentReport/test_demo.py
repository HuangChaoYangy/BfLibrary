import pytest
from pytest_assume.plugin import assume

@pytest.mark.parametrize(('x', 'y'),[(1, 2), (1, 0), (0, 1),(3, 3)])
def test_simple_assume(x, y):
    print("测试数据x=%s, y=%s" % (x, y))
    # 上下文管理器里面包含多个断言，则只有第一个会被执行
    with assume: assert x == y
    with assume: assert x+y > 1
    with assume: assert x > 1
    print("测试完成！")

if __name__ == "__main__":

    pytest.main(["test_demo.py",'-vs', '-q', '--alluredir', '../report/tmp', '--clean-alluredir'])
