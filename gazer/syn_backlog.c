// https://www.kernel.org/doc/htmldocs/networking/API-struct-sock.html

int kprobe__tcp_v4_syn_recv_sock(struct pt_regs *ctx, struct sock *sk){
    u32 pid = bpf_get_current_pid_tgid();
	// stash the sock ptr for lookup on return
	currsock.update(&pid, &sk);
	return 0;
};

int kretprobe__tcp_v4_syn_recv_sock(struct pt_regs *ctx){
    struct sock *newsk = (struct sock *)PT_REGS_RC(ctx);

    u32 pid = bpf_get_current_pid_tgid();

	struct sock **skpp;
	skpp = currsock.lookup(&pid);
	currsock.delete(&pid);
    if (skpp == 0) {
		return 0;	// missed entry
	}

    struct sock *skp = *skpp;

    backlog_key_t key = {};
    key.backlog = skp->sk_max_ack_backlog;
    key.saddr = newsk->__sk_common.skc_rcv_saddr;
    key.lport = newsk->__sk_common.skc_num;
    key.slot = bpf_log2l(skp->sk_ack_backlog);
    syn_backlog.atomic_increment(key);
    return 0;
}