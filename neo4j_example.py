from py2neo import Graph, Node, Relationship

# 连接到 Neo4j 数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "your_password"))

# 创建节点
person1 = Node("Person", name="Alice")
person2 = Node("Person", name="Bob")

# 创建关系
knows = Relationship(person1, "KNOWS", person2)

# 将节点和关系添加到数据库
graph.create(person1)
graph.create(person2)
graph.create(knows)

# 查询数据
query = "MATCH (p:Person)-[r:KNOWS]->(q:Person) RETURN p.name, r.type, q.name"
results = graph.run(query)

for record in results:
    print(record)