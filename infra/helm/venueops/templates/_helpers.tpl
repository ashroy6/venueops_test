{{- define "venueops.name" -}}
venueops
{{- end }}

{{- define "venueops.fullname" -}}
{{ include "venueops.name" . }}
{{- end }}

{{- define "venueops.labels" -}}
app.kubernetes.io/name: {{ include "venueops.name" . }}
app.kubernetes.io/managed-by: Helm
app.kubernetes.io/part-of: venueops-platform
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end }}

{{- define "venueops.selectorLabels" -}}
app.kubernetes.io/name: {{ include "venueops.name" . }}
app.kubernetes.io/part-of: venueops-platform
{{- end }}
