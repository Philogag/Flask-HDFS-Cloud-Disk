let Queue = (function () {

    const items = new WeakMap();//WeakMap对象是密钥/值对的集合，其中密钥被弱引用。键必须是对象，值可以是任意值。

    class Queue {

        constructor () {
            items.set(this, []);
        }

        push(element) {//向队列尾部添加一个（或多个）新的项
            let q = items.get(this);
            q.push(element);
        }

        pop() {//移除队列的第一个（排在队列最前面的）项，并返回被移除的元素。
            let q = items.get(this);
            let r = q.shift();
            return r;
        }

        front() {//返回队列中第一个元素——最先被添加，也将是最先被移除的元素。队列不做任何变动（不移除元素，只返回元素信息）
            let q = items.get(this);
            return q[0];
        }

        isEmpty(){//如果队列中不包含任何元素，返回true，否则返回false。
            return items.get(this).length == 0;
        }

        size(){//返回队列包含的元素个数，与数组的length属性类似。
            let q = items.get(this);
            return q.length;
        }

        clear(){//清空队列里面的元素。
            items.set(this, []);
        }

        print(){//打印队列为String到控制台
            console.log(this.toString());
        }

        toString(){//输出队列以String模式。
            return items.get(this).toString();
        }
    }
    return Queue;
})();