
connection: "biquery_publicdata_standard_sql" include: "/views/users.view.lkml"
include: "/views/order_items.view.lkml"
include: "/views/inventory_items.view.lkml"
include: "/views/products.view.lkml"
include: "/views/user_data.view.lkml"
include: "/views/events.view.lkml"
include: "/views/flights.view.lkml"
include: "/views/orders.view.lkml"
datagroup: the_look_default_datagroup {  max_cache_age: "1 hour" }
persist_with: the_look_default_datagroup 


explore: hugo_explore {
  join: users {
      type: left_outer
      sql_on: ${hugo_explore.user_id} = ${users.id} ;;
      relationship: many_to_one 
  } 
  from: events 
}
explore: flights {
}
explore: inventory_items {
  join: products {
      type: left_outer
      sql_on: ${inventory_items.product_id} = ${products.id} ;;
      relationship: many_to_one 
  } 
}
explore: order_items {
  join: orders {
      type: left_outer
      sql_on: ${order_items.order_id} = ${orders.id} ;;
      relationship: many_to_one 
  }
  join: inventory_items {
      type: left_outer
      sql_on: ${order_items.inventory_item_id} = ${inventory_items.id} ;;
      relationship: many_to_one 
  }
  join: users {
      type: left_outer
      sql_on: ${orders.user_id} = ${users.id} ;;
      relationship: many_to_one 
  }
  join: products {
      type: left_outer
      sql_on: ${inventory_items.product_id} = ${products.id} ;;
      relationship: many_to_one 
  } 
}
explore: orders {
  join: users {
      type: left_outer
      sql_on: ${orders.user_id} = ${users.id} ;;
      relationship: many_to_one 
  } 
}
explore: products {
  join: inventory_items {
      type: left_outer
      sql_on: ${products.inventory_item_id} = ${inventory_items.id} ;;
      relationship: many_to_one 
  } 
}
explore: saralooker {
  join: users {
      type: left_outer
      sql_on: ${saralooker.user_id} = ${users.id} ;;
      relationship: many_to_one 
  } 
}
explore: user_data {
  join: users {
      type: left_outer
      sql_on: ${user_data.user_id} = ${users.id} ;;
      relationship: many_to_one 
  } 
}
explore: users {
}