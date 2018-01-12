import lib.phplex as phplex
import lib.phpparse as yacc_parse
import translator.toflow as toflow
from itertools import tee, islice, chain
import pprint
import classifier.classifier as classifier
import drawer.drawer as fl_drawer

drawable_stack = []


# Parsing invocation
def parse_through_lex(file_path):
  data = open(file_path, 'r').read()
  phplex.full_lexer.input(data)
  return phplex.full_lexer


def recursive_parsing(nodes):
  if nodes is False:
    return

  # #print('inside the recursive parser')
  if toflow.is_leaf_node(nodes):
    # #print('leaf node', nodes)
    return nodes
  else:
    for node in nodes:
      if not toflow.is_leaf_node(node):
        #print('none leaf node:', node)
        #print()
        if isinstance(node, tuple):
          #print('tuple item')
          # recursive_parsing(toflow.get_child(toflow.get_node_type(node), toflow.get_node_attributes(node)))
          drawable = (toflow.identify_translate_to(node[0]), node)
          if drawable[0] is not False:
            drawable_stack.append(drawable)
          #print('drawable:', drawable_stack)
          processed_node = recursive_parsing(toflow.get_nodes(toflow.get_node_attributes(node)))
          # drawable_stack.append((toflow.get_node_typ(node), recursive_parsing(toflow.get_nodes(node))))
          # #print('processed_node:', processed_node)
        else:
          #print('list or dict or other item')
          processed_node = recursive_parsing(toflow.get_nodes(node))
          if processed_node is not None:
            drawable = toflow.identify_translate_to(processed_node[0]), processed_node
            # if drawable[0] is not False:
            #   drawable_stack.append(drawable)
            #print('drawable (from list):', drawable_stack)
          # #print('processed_node list:', processed_node)
          # drawable_stack.append((toflow.get_node_type(node), recursive_parsing(toflow.get_nodes(node))))

  return nodes

# Parsing
lexemes = parse_through_lex('./php_test_files/BasicClass.php')
parser = yacc_parse.make_parser()
parsed_ast = yacc_parse.run_parser(parser, open('./php_test_files/BasicClass.php', 'r'), True, False)

ast_processed = []
for statement in parsed_ast:
  if hasattr(statement, 'generic'):
    statement = statement.generic()
    ast_processed = statement

recursive_parsing(ast_processed)
# Test some imperative style coding
# yacc_parse.run_parser(parser, open('./php_test_files/Imperative.php', 'r'), False, False)

# Drawing the flow chart
# Drawer invocation
#print()
#print()
#print()
#print()
#print()
#print()



# For accessing previous/next elements in for loops
def previous_and_next(some_iterable):
  prevs, items, nexts = tee(some_iterable, 3)
  prevs = chain([None], prevs)
  nexts = chain(islice(nexts, 1, None), [None])
  return zip(prevs, items, nexts)


chart = None
x = fl_drawer.Drawer(chart)
for previous, drawing_entity, nxt in previous_and_next(drawable_stack):
  if drawing_entity[0] is False:
    continue

  if isinstance(drawing_entity, tuple):
    #print(drawing_entity)
    if drawing_entity[1][0] == 'If':
      item_name = 'If'
      getattr(x, drawing_entity[0])(item_name)
      #print('item value', toflow.get_node_values(drawing_entity[1]))
      # #print(drawing_entity[1][1]['expr'])
    else:
      item_name = 'echo ("' + drawing_entity[1][1]['nodes'][0] + '")'
      #print('item', drawing_entity[1])
      #print('item value', toflow.get_node_values(drawing_entity[1]))
      getattr(x, drawing_entity[0])(item_name)

  # Connection logic
  if previous is not None:
    x.connect('If', item_name, 'True')
  else:
    x.connect('Start', item_name)
  if nxt is None:
    x.end(item_name)
      # #print(drawing_entity[1][1]['nodes'])
  # drawing_entity[1][1]['nodes'] = 'an if condition'
x.get_drawing().write('../outputs/x.dot')
x.get_drawing().draw('../outputs/x.png', prog='circo')
