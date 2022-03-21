export const getResourceVersions = (resource: any) => {
    console.log(resource.data?.items?.map((item: any) => item.metadata.resourceVersion))
    return resource.data?.items?.map((item: any) => item.metadata.resourceVersion)
}