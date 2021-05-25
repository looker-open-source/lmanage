view: test_ndt {
  derived_table: {
    explore_source: order_items {
      column: total_revenue {}
      column: created_month {}
      column: user_id {}
    }
  }
  dimension: total_revenue {
    type: number
  }
  dimension: created_month {
    type: date_month
  }
  dimension: user_id {
    type: number
  }
}

