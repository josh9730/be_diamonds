from src import data


def test_parse_vendor_audit(fixture_audit_df):
    df = data.parse_vendor_audit(fixture_audit_df, ["VENDOR"], "2024-08-12", 10)

    assert list(df.columns) == ['Vendor', 'Video Link', 'Stock Number', 'Cert Number', 'Date']
    assert list(df['Stock Number']) == ['2000AF', '110A', '105A', '104A', '102A', '99A', '80A', '55C', '8F']
