pub mod graph {
    pub struct Graph {
        pub nodes : Vec<graph_items::node::Node>,
        pub edges : Vec<graph_items::edge::Edge>,
        pub attrs : Vec<(String, String)>
    }

    impl Graph {
        pub fn new() -> Self {
            Graph {
                nodes : vec![],
                edges : vec![],
                attrs : vec![]
            }
        }

        pub fn with_nodes(self, nodes: &Vec<graph_items::node::Node>) -> Self {
            Graph {
                nodes : nodes.to_vec(),
                edges : self.edges,
                attrs : self.attrs
            }
        }
    }

    pub mod graph_items {
        pub mod edge {
            pub struct Edge;
        }

        pub mod node {
            #[derive(PartialEq,Clone,Debug)]
            pub struct Node{
                label: String,
                attrs : Vec<(String, String)>
            }

            impl Node {
                pub fn new(label: &str) -> Self {
                    Node {
                        label : label.to_string(),
                        attrs : vec![]
                    }
                }

                pub fn with_attrs(mut self, attrs: &[(String, String)]) -> Self {
                    self.attrs.clone_from_slice(attrs);
                    self
                }
            }
        }
    }
}
