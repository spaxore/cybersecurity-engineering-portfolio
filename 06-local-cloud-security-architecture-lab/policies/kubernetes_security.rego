package kubernetes.security

deny contains msg if {
  input.kind == "Deployment"
  some container in input.spec.template.spec.containers
  not container.securityContext.runAsNonRoot
  msg := sprintf("container %q must set runAsNonRoot=true", [container.name])
}

deny contains msg if {
  input.kind == "Deployment"
  some container in input.spec.template.spec.containers
  container.securityContext.allowPrivilegeEscalation != false
  msg := sprintf("container %q must set allowPrivilegeEscalation=false", [container.name])
}

deny contains msg if {
  input.kind == "Deployment"
  some container in input.spec.template.spec.containers
  not container.securityContext.readOnlyRootFilesystem
  msg := sprintf("container %q must set readOnlyRootFilesystem=true", [container.name])
}
