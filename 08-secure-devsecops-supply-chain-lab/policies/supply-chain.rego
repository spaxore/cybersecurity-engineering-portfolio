package supplychain

deny contains "container must run as a non-root user" if {
    input.kind == "container"
    input.run_as_non_root != true
}

deny contains "container must define a health check" if {
    input.kind == "container"
    input.healthcheck_defined != true
}

deny contains "container must use a pinned base image tag" if {
    input.kind == "container"
    input.base_image_pinned != true
}

deny contains "dependency lock data must be present" if {
    input.kind == "application"
    input.dependency_lock_present != true
}
