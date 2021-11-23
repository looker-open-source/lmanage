explore: account {
  # Joins in this explore may be extended by other explores that want to include the account view
  # Be considerate of this when editing! Do not add one_to_many joins (e.g. opportunities)
  hidden: yes
  join: account_dnb_fields {
    view_label: "Account"
    sql: ;; #Field-only view
    relationship: one_to_one
  }
  join: account_next_renewal {
    sql_on: ${account_next_renewal.pk_account_id} = ${account.id} ;;
    relationship: one_to_one
  }
  join: next_renewal {
    from: opportunity
    relationship: one_to_one
    sql_on: ${next_renewal.id} = ${account_next_renewal.next_renewal_opp} ;;
  }
  join: metafore_prediction {
    view_label: "Next Renewal"
    relationship: one_to_one
    sql_on: ${metafore_prediction.pk1_opportnity_id} = ${next_renewal.id} ;;
    fields: [pk1_opportunity_id, renewal_prob]
  }

  join: account_team {
    view_label: "Account"
    sql_on: ${account_team.id} = ${account.account_manager_id} ;;
    relationship: many_to_one
    fields: [account_team.name]
  }
  join: opportunity_owner {
    view_label: "Account"
    relationship: many_to_one
    sql_on: ${account.owner_id} = ${opportunity_owner.id} ;;
    fields: [name]
  }
  join: renewal_manager {
    view_label: "Account"
    relationship: many_to_one
    sql_on: ${renewal_manager.id} = ${account.renewal_manager} ;;
    fields: [name]
  }

}

# Daniel Mintz
# 2019-04-19
# This hidden explore creates the account comparator
explore: account_comparator {
  hidden: yes

  # Switched to a persistent derived table that captures top 2000 comparisons for each account
  # It's a nested array structure, so needs to be unnested
  join: a1_a2_comparison {
    relationship: one_to_many
    sql: LEFT JOIN UNNEST(account_comparator.a2)  as a1_a2_comparison;;
  }

  join: account_1 {
    from: account
    relationship: one_to_one
    sql_on: ${account_comparator.account_1_cbit_id} = ${account_1.cbit_clearbit_c} ;;
    fields: [account_1.cbit_clearbit_c, account_1.account_status, account_1.owner_id,
             account_1.billing_country, account_1.billing_state, account_1.domain, account_1.industry, account_1.logo,
             account_1.logo_publicity, account_1.region, account_1.segment, account_1.type, account_1.current_customer,
             account_1.slack_channel_id, account_1.id]
    view_label: "Primary Account"
  }

  join: account_owner1 {
    from: account_owner
    sql_on: ${account_1.owner_id} = ${account_owner1.id} ;;
    relationship: many_to_one
    fields: [account_owner1.name]
    view_label: "Primary Account"
  }

  join: cbit_clearbit1 {
    from: cbit_clearbit
    fields: [cbit_clearbit1.companydescription_c]
    relationship: one_to_one
    sql_on: ${account_comparator.account_1_cbit_id} = ${cbit_clearbit1.id} ;;
    view_label: "Primary Account"
  }

  join: account_2 {
    from: account
    relationship: one_to_one
    sql_on: ${a1_a2_comparison.account_2_cbit_id} = ${account_2.cbit_clearbit_c} ;;
    view_label: "Comparison Accounts"
    fields: [account_2.cbit_clearbit_c, account_2.account_name, account_2.account_status, account_2.owner_id,
             account_2.billing_country, account_2.billing_state, account_2.domain, account_2.industry, account_2.logo,
             account_2.logo_publicity, account_2.region, account_2.segment, account_2.type, account_2.current_customer,
             account_2.slack_channel_id, account_2.id]
  }

  join: account_owner2 {
    from: account_owner
    sql_on: ${account_2.owner_id} = ${account_owner2.id} ;;
    relationship: many_to_one
    fields: [account_owner2.name]
    view_label: "Comparison Accounts"
  }

  join: cbit_clearbit2 {
    from: cbit_clearbit
    fields: [cbit_clearbit2.companydescription_c]
    relationship: one_to_one
    sql_on: ${a1_a2_comparison.account_2_cbit_id} = ${cbit_clearbit2.id} ;;
    view_label: "Comparison Accounts"
  }


}


explore: ooo {
  label: "OOO"
  hidden: yes
  join: dcl_people_and_roles {
    sql_on: ${ooo.sha_email} = ${dcl_people_and_roles.sha_email} ;;
    relationship: many_to_one
    type: left_outer
    fields: [core*]
  }
}

explore: ga_customized_sessions {
  hidden: yes
  label: "GA Sessions with SFDC"
  extends: [ga_sessions_block]

  join: ga_sfdc_user_map {
    type: left_outer
    relationship: many_to_one
    sql_on: ${ga_sfdc_user_map.ga_client_id} = ${ga_sessions.client_id} ;;
  }

  join: lead {
    type: left_outer
    relationship: many_to_one
    sql_on: ${ga_sfdc_user_map.lead_id} = ${lead.id} ;;
  }

  join: opportunity_owner {
    type: left_outer
    relationship: many_to_one
    sql_on: ${lead.owner_id} = ${opportunity_owner.id};;
  }

  join: user_role {
    type: left_outer
    relationship: many_to_one
    sql_on: ${opportunity_owner.user_role_id} = ${user_role.id};;
  }

  join: contact {
    type: left_outer
    relationship: many_to_one
    sql_on: ${ga_sfdc_user_map.contact_id} = ${contact.id};;
  }

  join: user_email_bqs {
    view_label: "Contact"
    fields: [email*]
    type: left_outer
    relationship: many_to_one
    sql_on: ${user_email_bqs.sha_email} = ${contact.sha_email} ;;
  }

  join: account_contact_role {
    type: left_outer
    relationship: many_to_many
    sql_on: ${contact.id} = ${account_contact_role.contact_id} ;;
    fields: []
  }

  join: account {
    type: left_outer
    relationship: many_to_one
    sql_on: ${account_contact_role.account_id} = ${account.id} ;;
  }
}

explore: opportunity_line_item_schedule {
  hidden: yes
  join: opportunity_line_item {
    type: left_outer
    sql_on: ${opportunity_line_item_schedule.opportunity_line_item_id} = ${opportunity_line_item.id} ;;
    relationship: many_to_one
  }

  join: product_2 {
    from: product
    type: left_outer
    sql_on: ${opportunity_line_item.product_2_id} = ${product_2.id} ;;
    relationship: many_to_one
  }

  join: opportunity {
    type: left_outer
    sql_on: ${opportunity_line_item.opportunity_id} = ${opportunity.id} ;;
    relationship: many_to_one
  }

  join: pricebook_entry {
    type: left_outer
    sql_on: ${opportunity_line_item.pricebook_entry_id} = ${pricebook_entry.id} ;;
    relationship: many_to_one
  }

  join: account {
    type: left_outer
    sql_on: ${opportunity.account_id} = ${account.id} ;;
    relationship: many_to_one
  }
}

explore: subscription_line_item {
  view_label: "[Subscription Line Items]"
  join: product {
    type: left_outer
    relationship: many_to_one
    sql_on: ${product.id} = ${subscription_line_item.product_2_id};;
  }
  join: subscription {
    type: full_outer
    relationship: many_to_one
    sql_on: ${subscription_line_item.parent_id} = ${subscription.id} ;;
  }
  join: account {
    type: left_outer
    relationship: many_to_one
    sql_on: ${subscription.account_id} = ${account.id} ;;
  }
}

explore: attribution_maca_data {
  sql_preamble:
CREATE TEMP FUNCTION
  get_negative_segments(json STRING)
  RETURNS ARRAY<STRING>
  LANGUAGE js AS """
    if (json ===null){
        return []
    }
    return (
        JSON.parse(json)
            .filter(obj => obj.operation === 'EXCLUDE')
            .map(obj => obj.segment_id)
            .reduce((prev,curr) => prev.concat(curr),[])
            .filter(x => !!x)
    )
""";
  ;;
}
