# file: app.py
import streamlit as st
import requests
import re

st.title("Reverb Draft Creator (No Photos)")

st.markdown("""
Enter your Reverb API token and the listing URL to create a draft copy of an existing listing.
""")

token = st.text_input("API Token", type="password")
url = st.text_input("Reverb Listing URL")

if st.button("Create Draft"):
    if not token or not url:
        st.error("Please provide both API token and listing URL.")
    else:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept-Version": "3.0",
            "Content-Type": "application/hal+json",
            "Accept": "application/hal+json",
        }

        listing_id = None
        if "reverb.com/item/" in url:
            part = url.split("/item/")[1].split("?")[0]
            m = re.match(r"^(\d+)", part)
            if m:
                listing_id = m.group(1)

        if not listing_id:
            st.error("Invalid Reverb listing URL.")
        else:
            st.info(f"Fetching listing details for ID: {listing_id}...")
            r = requests.get(f"https://api.reverb.com/api/listings/{listing_id}", headers=headers)
            if r.status_code != 200:
                st.error(f"Failed to fetch listing: {r.status_code}")
            else:
                listing = r.json()
                title = listing.get("title", "")
                description = listing.get("description", "")
                make = listing.get("make", "")
                model = listing.get("model", "")
                price = listing.get("price", {}).get("amount", "1.00")

                payload = {
                    "title": title,
                    "description": description,
                    "brand": make,
                    "model": model,
                    "price": {"amount": price, "currency": "USD"},
                    "state": "draft",
                }

                st.info("Creating draft...")
                draft = requests.post(
                    "https://api.reverb.com/api/listings", headers=headers, json=payload
                )
                if draft.status_code not in [200, 201]:
                    st.error(f"Draft creation failed: {draft.status_code}")
                    st.code(draft.text)
                else:
                    draft_data = draft.json()
                    draft_id = draft_data.get("id") or draft_data.get("listing", {}).get("id")
                    if not draft_id:
                        st.error("Draft ID not found in response.")
                    else:
                        st.success(f"✅ Draft created successfully! ID: {draft_id}")
