

pub mod graph {
    use graph_items::node::Node;
    use graph_items::edge::Edge;
    use std::collections::HashMap;

    #[derive(Default)]
    pub struct Graph {
        pub nodes : Vec<Node>,
        pub edges : Vec<Edge>,
        pub attrs : HashMap<String,String>,
    }

    impl Graph {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn with_nodes(mut self, nodes: &Vec<Node>) -> Self {
            self.nodes = nodes.to_vec();
            self
        }

        pub fn with_edges(mut self, edges: &Vec<Edge>) -> Self {
            self.edges = edges.to_vec();
            self
        }

        pub fn with_attrs(mut self, attrs: &[(&str, &str)]) -> Self {
            self.attrs = attrs.iter().map(|(key, value)| (key.to_string(), value.to_string())).collect();
            self
        }

        pub fn get_node(self, name: &str ) -> Option<Node> {
            self.nodes.into_iter().find(|x| x.label == name)
        }

    }

    pub mod graph_items {

        pub mod edge {
            use std::collections::HashMap;

            #[derive(PartialEq,Clone,Debug)]
            pub struct Edge {
                pub start : String,
                pub end : String,
                pub attrs : HashMap<String, String>,
            }

            impl Edge {
                pub fn new(start: &str, end: &str) -> Self {
                    Edge{
                        start: start.to_string(),
                        end: end.to_string(),
                        attrs: HashMap::new(),
                    }
                }

                pub fn with_attrs(mut self, attrs: &[(&str, &str)]) -> Self {
                    self.attrs = attrs.iter().map(|(key, value)| (key.to_string(), value.to_string())).collect();
                    self
                }
            }
        }

        pub mod node {
            use std::collections::HashMap;

            #[derive(PartialEq,Clone,Debug)]
            pub struct Node{
                pub label : String,
                pub attrs : HashMap<String, String>
            }

            impl Node {
                pub fn new(label: &str) -> Self {
                    Node {
                        label : label.to_string(),
                        attrs : HashMap::new()
                    }
                }

                pub fn with_attrs(mut self, attrs: &[(&str, &str)]) -> Self {
                    self.attrs = attrs.iter().map(|(key, value)| (key.to_string(), value.to_string())).collect();
                    self
                }

                pub fn get_attr(&self, key: &str) -> Option<&str> {
                    self.attrs.get(key).map(|value| &**value)
                }
            }
        }
    }
}
