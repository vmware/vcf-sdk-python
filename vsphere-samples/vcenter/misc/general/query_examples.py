# Copyright (c) 2025 Broadcom. All Rights Reserved.
# Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
# and/or its subsidiaries.

from pyVmomi import vim, vmodl
from vcf.vsphere_utils.query import QueryBuilder, QueryPredicateBuilder, QueryResult
from helpers import cli, service_instance
from json import dumps

ResourceType = vim.SearchIndex.QuerySpec.ResourceType


def print_table(data, headers=None):
    """
    Print a table with headers and values in grid format without using 
    external modules.
    
    Args:
        data: List of lists containing table data
        headers: List of header strings (optional)
    """
    if not data:
        print("No data to display")
        return
    
    # Calculate column widths
    if headers:
        col_widths = [len(str(header).expandtabs(4)) 
                      for header in headers]
    else:
        col_widths = [0] * len(data[0]) if data else []
    
    # Find maximum width for each column
    for row in data:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                cell_str = str(cell)
                # Split by newlines and find the longest line
                lines = cell_str.split('\n')
                max_line_len = max(len(line.expandtabs(4)) 
                                   for line in lines)
                col_widths[i] = max(col_widths[i], max_line_len)
    
    # Add padding
    col_widths = [width + 2 for width in col_widths]
    
    # Print top border
    print('+' + '+'.join('-' * width for width in col_widths) + '+')
    
    # Print headers if provided
    if headers:
        header_row = '|'
        for i, header in enumerate(headers):
            if i < len(col_widths):
                header_str = str(header)
                # Only use first line of multi-line headers
                first_line = header_str.split('\n')[0]
                header_row += f' {first_line:<{col_widths[i]-1}}|'
        print(header_row)
        print('+' + '+'.join('-' * width for width in col_widths) + '+')
    
    # Print data rows
    for row in data:
        # Split each cell by newlines
        cell_lines = [str(cell).split('\n') for cell in row]
        max_lines = max(len(lines) for lines in cell_lines)
        
        # Print each line of the row
        for line_idx in range(max_lines):
            data_row = '|'
            for i, lines in enumerate(cell_lines):
                if i < len(col_widths):
                    content = lines[line_idx] if line_idx < len(lines) else ''
                    data_row += f' {content:<{col_widths[i]-1}}|'
            print(data_row)
        print('+' + '+'.join('-' * width for width in col_widths) + '+')

def print_result_as_table(query_result: QueryResult):
    actual_result = query_result.GetResult()
    headers = actual_result.properties
    rows = []
    for item in actual_result.items:
        row = []
        for value in item.propertyValues:
            actual_value = value.value
            if isinstance(actual_value, list):
                try:
                    if all(
                        [isinstance(x, vim.SearchIndex.OptionalValue)
                         for x in actual_value_el]
                            for actual_value_el in actual_value):
                        actual_value = dumps([
                            [x.value for x in actual_value_el]
                            for actual_value_el in actual_value], indent=4)
                except TypeError:
                    pass
                except AttributeError:
                    pass
            row.append(str(actual_value))
        rows.append(row)
    print_table(rows, headers=headers)
    if actual_result.totalCount:
        print("Total Count:", actual_result.totalCount)
    if query_result.HasNextPage():
        print("More pages present")

def print_query_result(query_result: QueryResult, print_as_table: bool):
    """
    Helper function to print query results either as a table or as raw data.
    
    Args:
        query_result: QueryResult object to print
        print_as_table: If True, print as formatted table; if False, 
                        print raw result
    """
    if print_as_table:
        print_result_as_table(query_result)
    else:
        # Print the actual return value of Execute
        result = query_result.GetResult()
        print("Query Result:")
        print(f"Properties: {result.properties}")
        print(f"Total Count: {result.totalCount}")
        print(f"Items count: {len(result.items)}")
        print("Items:")
        for i, item in enumerate(result.items):
            print(f"  Item {i}:")
            for j, prop_value in enumerate(item.propertyValues):
                print(f"    {result.properties[j]}: {prop_value.value}")

def main():
    """
    Main function that demonstrates various query examples using the 
    QueryBuilder.
    """
    parser = cli.Parser()
    parser.add_custom_argument('--query-example-num', type=int, default=1, 
                              help='Example number to run (1-22)')
    parser.add_custom_argument('--query-host-id', type=str, default='host-9', 
                              help='Host name for specific host queries '
                                   '(Examples 3, 4)')
    parser.add_custom_argument('--query-svga-value', type=str, default='FALSE', 
                              help='Extra config value for VM queries '
                                   '(Example 6)')
    parser.add_custom_argument('--query-pnic-key', type=str, 
                              default='key-vim.host.PhysicalNic-vmnic0', 
                              help='Physical NIC key for host network queries '
                                   '(Examples 8, 9)')
    parser.add_custom_argument('--query-mac-address', type=str, 
                              default='02:00:53:58:79:89', 
                              help='MAC address for specific host pnic queries '
                                   '(Example 13)')
    parser.add_custom_argument('--query-min-link-speed', type=int, default=10, 
                              help='Minimum link speed for all pnics query '
                                   '(Example 14, 15)')
    parser.add_custom_argument('--query-vm-name-pattern', type=str, 
                              default='*clone*', 
                              help='VM name pattern for like queries '
                                   '(Examples 16, 17)')
    parser.add_custom_argument('--query-vm-names', type=str, nargs='+', 
                              default=['cloneVM-1', 'VM-4'], 
                              help='List of VM names for IN queries '
                                   '(Examples 18, 19)')
    parser.add_custom_argument('--query-folder-name-pattern', type=str, 
                              default='tst-folder*', 
                              help='Folder name pattern for like queries '
                                   '(Examples 20, 21, 22)')
    parser.add_custom_argument('--query-pagination-limit', type=int, default=5, 
                              help='Limit for pagination example (Example 21)')
    parser.add_custom_argument('--print-as-table', action='store_true', 
                              default=False,
                              help='Print results as table (default: True)')
    args = parser.get_args()
    
    try:
        si = service_instance.connect(args)
    except Exception as ex:
        print(f"Failed to connect: {ex}")
        return -1

    # Example selector
    example_num = args.query_example_num
    
    try:
        if example_num == 1:
            print("=== Example 1: Basic VM listing ===")
            print_query_result(QueryBuilder(si).Select("@moRef", "name").From(
                ResourceType.VirtualMachine).Execute(), args.print_as_table)
    
        elif example_num == 2:
            print("=== Example 2: VMs with power state and host ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", "summary.runtime.powerState",
                "summary.runtime.host").From(
                ResourceType.VirtualMachine).Execute(), 
                args.print_as_table)
        
        elif example_num == 3:
            print("=== Example 3: VMs on specific host ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", "summary.runtime.powerState",
                "summary.runtime.host").From(ResourceType.VirtualMachine).Where(
                QueryPredicateBuilder("summary.runtime.host").Equal(
                    vim.HostSystem(args.query_host_id))).Execute(), 
                args.print_as_table)
        
        elif example_num == 4:
            print("=== Example 4: Powered off VMs on specific host ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", "summary.runtime.powerState",
                "summary.runtime.host").From(ResourceType.VirtualMachine).Where(
                QueryPredicateBuilder("summary.runtime.host").Equal(
                    vim.HostSystem(args.query_host_id))).Where(
                QueryPredicateBuilder("summary.runtime.powerState").Equal(
                    "poweredOff")).Execute(), args.print_as_table)
        
        elif example_num == 5:
            print("=== Example 5: VMs with svga.present config ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", "config.extraConfig[\"svga.present\"]").From(
                ResourceType.VirtualMachine).Execute(), args.print_as_table)
        
        elif example_num == 6:
            print("=== Example 6: VMs with svga.present=FALSE ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", "config.extraConfig[\"svga.present\"]").From(
                ResourceType.VirtualMachine).Where(
                QueryPredicateBuilder("config.extraConfig[\"svga.present\"]").
                Equal(args.query_svga_value)).Execute(), args.print_as_table)
        
        elif example_num == 7:
            print("=== Example 7: Host network pnic ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", "config.network.pnic").From(
                ResourceType.HostSystem).Execute(), args.print_as_table)
        
        elif example_num == 8:
            print("=== Example 8: Host specific pnic ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", 
                f"config.network.pnic[\"{args.query_pnic_key}\"]").From(
                ResourceType.HostSystem).Execute(), args.print_as_table)
        
        elif example_num == 9:
            print("=== Example 9: Host pnic MAC address ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", 
                f"config.network.pnic[\"{args.query_pnic_key}\"].mac").From(
                ResourceType.HostSystem).Execute(), args.print_as_table)
        
        elif example_num == 10:
            print("=== Example 10: All host pnic MAC addresses ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", "config.network.pnic[*].mac").From(
                ResourceType.HostSystem).Execute(), args.print_as_table)
        
        elif example_num == 11:
            print("=== Example 11: Host pnic keys and MACs ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", "config.network.pnic[*].mac", 
                "config.network.pnic[*].key").From(
                ResourceType.HostSystem).Execute(), 
                args.print_as_table)
        
        elif example_num == 12:
            print("=== Example 12: Host pnic details (key, mac, speed) ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", 
                "config.network.pnic[*].(key,mac,linkSpeed.speedMb)").From(
                ResourceType.HostSystem).Execute(), args.print_as_table)
        
        elif example_num == 13:
            print("=== Example 13: Host with specific MAC address ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name", 
                "config.network.pnic[*].(key,mac,linkSpeed.speedMb)").From(
                ResourceType.HostSystem).Where(
                QueryPredicateBuilder("config.network.pnic[*].mac").
                AnyArrayElement().Equal(args.query_mac_address)).Execute(), 
                args.print_as_table)
        
        elif example_num == 14:
            print("=== Example 14: Hosts with all pnics > query_min_link_speed Mbps ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name",
                "config.network.pnic[*].(key,mac,linkSpeed.speedMb)").From(
                vim.SearchIndex.QuerySpec.ResourceType.HostSystem).Where(
                QueryPredicateBuilder(
                    "config.network.pnic[*].linkSpeed.speedMb").
                AllArrayElements().Greater(
                    args.query_min_link_speed)).Execute(), 
                args.print_as_table)
        
        elif example_num == 15:
            print("=== Example 15: Hosts with any pnic > query_min_link_speed Mbps ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name",
                "config.network.pnic[*].(key,mac,linkSpeed.speedMb)").From(
                vim.SearchIndex.QuerySpec.ResourceType.HostSystem).Where(
                QueryPredicateBuilder(
                    "config.network.pnic[*].linkSpeed.speedMb").
                AnyArrayElement().Greater(
                    args.query_min_link_speed)).Execute(), 
                args.print_as_table)
        
        elif example_num == 16:
            print("=== Example 16: VMs with names like '*clone*' ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name").From(ResourceType.VirtualMachine).Where(
                QueryPredicateBuilder("name").Like(
                    args.query_vm_name_pattern)).Execute(), 
                args.print_as_table)
        
        elif example_num == 17:
            print("=== Example 17: VMs with names NOT like '*clone*' ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name").From(ResourceType.VirtualMachine).Where(
                QueryPredicateBuilder("name").NotLike(
                    args.query_vm_name_pattern)).Execute(), 
                args.print_as_table)
        
        elif example_num == 18:
            print("=== Example 18: VMs with specific names ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name").From(ResourceType.VirtualMachine).Where(
                QueryPredicateBuilder("name").In(
                    *args.query_vm_names)).Execute(), 
                args.print_as_table)
        
        elif example_num == 19:
            print("=== Example 19: VMs with names NOT in specific list ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name").From(ResourceType.VirtualMachine).Where(
                QueryPredicateBuilder("name").NotIn(
                    *args.query_vm_names)).Execute(), 
                args.print_as_table)
        
        elif example_num == 20:
            print("=== Example 20: Folders with names like 'tst-folder*' ===")
            print_query_result(QueryBuilder(si).Select(
                "@moRef", "name").From(ResourceType.Folder).Where(
                QueryPredicateBuilder("name").Like(
                    args.query_folder_name_pattern)).Execute(), 
                args.print_as_table)
        
        elif example_num == 21:
            print("=== Example 21: Pagination example ===")
            ret = QueryBuilder(si).Select(
                "@moRef", "name").From(ResourceType.Folder).Where(
                QueryPredicateBuilder("name").Like(
                    args.query_folder_name_pattern)).Limit(
                args.query_pagination_limit).Execute()

            page_no = 0
            while True:
                page_no += 1
                print("Page:", page_no)
                print_query_result(ret, args.print_as_table)
                if not ret.HasNextPage():
                    break
                ret = ret.GetNextPage()
        
        elif example_num == 22:
            print("=== Example 22: Count folders ===")
            print_query_result(QueryBuilder(si).Select().From(
                ResourceType.Folder).Limit(0).Where(
                QueryPredicateBuilder("name").Like(
                    args.query_folder_name_pattern)).ReturnTotalCount().Execute(), 
                args.print_as_table)
        
        else:
            print(f"Invalid example number: {example_num}")
            print("Valid examples: 1-22")
            return -1

    except vmodl.MethodFault as ex:
        print(f"Caught vmodl fault: {ex}")
        return -1
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        return -1
    print("Query examples completed successfully")
    return 0


if __name__ == "__main__":
    main()