# -*- coding: utf-8 -*-
from tabulate import tabulate
import re

from omg.common.helper import age, extract_labels


# Special function to output node
# Generate output table if -o not set or 'wide'
# We will create an array of array and then print if with tabulate
def node_out(t, ns, res, output, show_type, show_labels):
    output_nodes = []
    # header
    # we will append the header array at last after sorting
    if output == "wide" and not show_labels:
        header = [
            "NAME",
            "STATUS",
            "ROLES",
            "AGE",
            "VERSION",
            "INTERNAL-IP",
            "EXTERNAL-IP",
            "OS-IMAGE",
            "KERNEL-VERSION",
            "CONTAINER-RUNTIME",
        ]
    elif output == "wide" and show_labels:
        header = [
            "NAME",
            "STATUS",
            "ROLES",
            "AGE",
            "VERSION",
            "INTERNAL-IP",
            "EXTERNAL-IP",
            "OS-IMAGE",
            "KERNEL-VERSION",
            "CONTAINER-RUNTIME",
            "LABELS",
        ]
    elif show_labels:
        header = ["NAME", "STATUS", "ROLES", "AGE", "VERSION", "LABELS"]
    else:
        header = ["NAME", "STATUS", "ROLES", "AGE", "VERSION", "vCPU", "MEM", "DISK", "maxPods", "osImage"]
    # pods
    for node in res:
        n = node["res"]

        cpu = n["status"]["capacity"]["cpu"]
        memory = n["status"]["capacity"]["memory"]
        ephemeral_storage = n["status"]["capacity"]["ephemeral-storage"]
        pods = n["status"]["capacity"]["pods"]
        osImage = n["status"]["nodeInfo"]["osImage"]

        if re.search ("Ki$", memory):
            memory = memory.strip ("Ki")
            memory = "%.2f" % (int (memory) / 1024 / 1024) 
            memory = str (memory) + ' Gi'

        if re.search ("Ki$", ephemeral_storage):
            ephemeral_storage = ephemeral_storage.strip ("Ki")
            ephemeral_storage = "%.2f" % (int (ephemeral_storage) // 1024 // 1024) 
            ephemeral_storage = str (ephemeral_storage) + ' Gi'

        osImage = osImage.replace ("Red Hat Enterprise Linux CoreOS", 'CoreOS')

        row = []
        # name
        if show_type:
            row.append(t + "/" + n["metadata"]["name"])
        else:
            row.append(n["metadata"]["name"])
        # status
        ready = next(
            c["status"] for c in n["status"]["conditions"] if c["type"] == "Ready"
        )
        if ready == "True":
            status = "Ready"
        else:
            status = "NotReady"
        if "unschedulable" in n["spec"] and n["spec"]["unschedulable"]:
            status += ",SchedulingDisabled"
        row.append(status)
        # roles
        roles = []
        for label in n["metadata"]["labels"]:
            if label.startswith("node-role.kubernetes.io/"):
                roles.append(label.split("/")[1])
        row.append(",".join(roles))
        # age
        ct = str(n["metadata"]["creationTimestamp"])
        ts = node["gen_ts"]
        row.append(age(ct, ts))
        # version
        ver = n["status"]["nodeInfo"]["kubeletVersion"]
        row.append(ver)
        row.append (cpu)
        row.append (memory)
        row.append (ephemeral_storage)
        row.append (pods)
        row.append (osImage)
        if output == "wide":
            # internal/external ip
            i_ip = "<none>"
            e_ip = "<none>"
            addresses = n["status"]["addresses"]
            for a in addresses:
                if a["type"] == "InternalIP":
                    i_ip = a["address"]
                if a["type"] == "ExternalIP":
                    e_ip = a["address"]
            row.append(i_ip)
            row.append(e_ip)
            # os-image
            osimg = n["status"]["nodeInfo"]["osImage"]
            row.append(osimg)
            # kernelVersion
            kver = n["status"]["nodeInfo"]["kernelVersion"]
            row.append(kver)
            crt = n["status"]["nodeInfo"]["containerRuntimeVersion"]
            row.append(crt)
        # show-labels
        if show_labels:
            row.append(extract_labels(n))

        output_nodes.append(row)

    # sort by 2nd column (role)
    sorted_output = sorted(output_nodes, key=lambda x: x[2])
    sorted_output.insert(0, header)

    print(tabulate(sorted_output, tablefmt="jira", headers="firstrow"))
