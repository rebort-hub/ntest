import { systemTitle } from '@/config'

export function changeTitle(name: any) {
  // document.title = `${name}-${systemTitle}`
  document.title = `${name}-${localStorage.getItem("platform_name") || systemTitle}`
}
