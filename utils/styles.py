TABLE_CSS = """
<style>
    .styled-table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        min-width: 400px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }
    .styled-table thead tr {
        background-color: #009879;
        color: #ffffff;
        text-align: left;
    }
    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
        text-align: center;
        color: #222222 !important;
        background-color: #ffffff;
    }
    .styled-table tbody tr td:first-child {
        text-align: left;
        padding-left: 15px;
    }
    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
        background-color: #ffffff;
    }
    .styled-table tbody tr:nth-of-type(even) td {
        background-color: #f3f3f3;
    }
    .styled-table tbody tr.summary-row td {
        font-weight: bold;
        color: #009879 !important;
        background-color: #e8f5e9;
        border-bottom: 2px solid #009879;
    }
    .styled-table tbody tr.new-asset-row td {
        background-color: #fff9e6;
        color: #c07c00 !important;
        font-style: italic;
    }
</style>
"""
