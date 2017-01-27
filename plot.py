#!/usr/bin/env python

import sys, os, getopt
import operator
import csv


def format_csvline(*args):
    line = ",".join(map(str, args))
    line += "\n"
    return line


def sortcat_csv(filename, col, cat):
    csv_file = open(filename, "r")
    reader = csv.reader(csv_file, delimiter=",")
    
    sorted_list = sorted(reader, key=operator.itemgetter(col), reverse=True)

    output = open(filename + "_sortcat_" + str(cat), "w")

    for i in range(cat):
        line = format_csvline(sorted_list[i])
        output.write(line)

    output.close()
    csv_file.close()

# Processes dns data up to rank k into dictionary form
def process(dns_file, k):
    data_file = open(dns_file, "r")

    dns_sitelist = {}
    site_dnslist = {}

    for line in data_file:
        line = line.strip(',\n\r')
        line = line.split(',')

        # line = [rank, site, dns]
        rank = int(line[0])
        if rank > k: break

        site = line[1]
        dns = line[2]

        # dns_sitelist: dns as key
        if dns in dns_sitelist:
            dns_sitelist[dns].append(site)
        else:
            dns_sitelist[dns] = [site]

        # site_dnslist: site as key
        if site in site_dnslist:
            site_dnslist[site].append(dns)
        else:
            site_dnslist[site] = [dns]

    data_file.close()

    return (dns_sitelist, site_dnslist)


def dns_robustcount(dns_file, k):
    (dns_sitelist, site_dnslist) = process(dns_file, k)

    dns_robust = {} # dns: [robust_count, nonrobust_count]

    for dns in dns_sitelist:
        for site in dns_sitelist[dns]:

            if not site in site_dnslist:
                sys.exit("dns_robustcount(): incompatible data\n")
    

            site_outdegree = len(site_dnslist[site])
            if site_outdegree < 1:
                sys.exit("dns_robustcount(): site without dns found\n")

            elif site_outdegree == 1:
                # not robust
                if not dns in dns_robust:
                    dns_robust[dns] = [0,1]
                else:
                    dns_robust[dns][1] += 1
    
            else: #site_outdegree >= 1
                # robust
                if not dns in dns_robust:
                    dns_robust[dns] = [1,0]
                else:
                    dns_robust[dns][0] +=1


    # Output results
    filename = "dns_robustcount_" + str(k)
    with open("results/" + filename, "w") as f:
        f.write("\n")
        for dns in dns_robust:
            robust_count = dns_robust[dns][0]
            nonrobust_count = dns_robust[dns][1]
            total = robust_count + nonrobust_count

            line = format_csvline(dns, total, robust_count, nonrobust_count)
            f.write(line)


def main(argv):
    # Parse command line arguments
    if len(sys.argv) < 3:
        sys.exit("Usage: ./plot.py <filename> <command> <k1> [k2]")

    filename = sys.argv[1]
    command = sys.argv[2]
    k1 = int(sys.argv[3])
    k2 = 0
    
    try:
        k2 = int(sys.argv[4])
    except:
        pass


    # Create results directory
    dir = os.path.dirname(__file__)
    results_dir = os.path.join(dir, 'results')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Execute
    if command == "robust":
        dns_robustcount(filename, k1)

    elif command == "sortcat":
        sortcat_csv(filename, k1, k2)

    print "Execution complete."



if __name__ == "__main__":
    main(sys.argv[1:])