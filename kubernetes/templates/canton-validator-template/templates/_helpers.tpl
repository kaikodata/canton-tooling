{{/*
Expand the name of the chart.
*/}}

{{- define "service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "checkNamespace" -}}
{{- if not .Values.namespace }}
{{- fail "Error: The 'namespace' value is required but not set." }}
{{- end }}
{{- end }}

{{- define "checkEnvironment" -}}
{{- if not (or (eq .Values.environment "staging-priv") (eq .Values.environment "production-us-priv") (eq .Values.environment "production-eu-priv")) }}
{{- fail "Error: 'environment' is not defined. It must be either 'production-us', 'staging', 'staging-priv', or 'production-eu'" }}
{{- end }}
{{- end }}

{{- define "subdomain" -}}
{{- if eq .Values.environment "production-us-priv" }}
{{- printf "" -}}
{{- else if eq .Values.environment "production-eu-priv" }}
{{- printf "eu." -}}
{{- else if eq .Values.environment "staging-priv" }}
{{- printf "stg." -}}
{{- end }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "service.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Common labels
*/}}
{{- define "pod.labels" -}}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/name: {{ .Values.name }}
{{- if or .Chart.AppVersion .Values.imageTag }}
app.kubernetes.io/version: {{ .Values.imageTag | default .Chart.AppVersion | trunc 63 | quote }}
{{- end }}
{{- if .Values.serviceType }}
serviceType: {{ .Values.serviceType | quote }}
{{- end }}
{{- end }}

{{- define "service.labels" -}}
helm.sh/chart: {{ printf "canton-validator-template-%s" .Chart.Version }}
{{ include "pod.labels" . }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "service.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "service.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
